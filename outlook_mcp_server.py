import datetime
import os
import win32com.client
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
import pythoncom

# Initialize FastMCP server
mcp = FastMCP("outlook-assistant")

# Constants
MAX_DAYS = 30
# Email cache for storing retrieved emails by number
email_cache = {}

# Helper functions
def connect_to_outlook():
    """Connect to Outlook application using COM"""
    try:
         pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)  # <-- This line is the fix!
         outlook = win32com.client.Dispatch("Outlook.Application")
         namespace = outlook.GetNamespace("MAPI")
         return outlook, namespace
    except Exception as e:
        raise Exception(f"Failed to connect to Outlook: {str(e)}")


def get_folder_by_name(namespace, folder_name: str):
    """Get a specific Outlook folder by name"""
    try:
        # First check inbox subfolder
        inbox = namespace.GetDefaultFolder(6)  # 6 is the index for inbox folder
        
        # Check inbox subfolders first (most common)
        for folder in inbox.Folders:
            if folder.Name.lower() == folder_name.lower():
                return folder
                
        # Then check all folders at root level
        for folder in namespace.Folders:
            if folder.Name.lower() == folder_name.lower():
                return folder
            
            # Also check subfolders
            for subfolder in folder.Folders:
                if subfolder.Name.lower() == folder_name.lower():
                    return subfolder
                    
        # If not found
        return None
    except Exception as e:
        raise Exception(f"Failed to access folder {folder_name}: {str(e)}")


def format_email(mail_item) -> Dict[str, Any]:
    """Format an Outlook mail item into a structured dictionary with To and CC separated."""
    try:
        to_recipients = []
        cc_recipients = []

        if mail_item.Recipients:
            for i in range(1, mail_item.Recipients.Count + 1):
                recipient = mail_item.Recipients(i)
                try:
                    recipient_str = f"{recipient.Name} <{recipient.Address}>"
                except:
                    recipient_str = recipient.Name
                
                if recipient.Type == 1:  # To
                    to_recipients.append(recipient_str)
                elif recipient.Type == 2:  # CC
                    cc_recipients.append(recipient_str)

        email_data = {
            "id": mail_item.EntryID,
            "conversation_id": getattr(mail_item, 'ConversationID', None),
            "subject": mail_item.Subject,
            "sender": mail_item.SenderName,
            "sender_email": mail_item.SenderEmailAddress,
            "received_time": mail_item.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S") if mail_item.ReceivedTime else None,
            "to": to_recipients,
            "cc": cc_recipients,
            "body": mail_item.Body,
            "has_attachments": mail_item.Attachments.Count > 0 if hasattr(mail_item, 'Attachments') else False,
            "attachment_count": mail_item.Attachments.Count if hasattr(mail_item, 'Attachments') else 0,
            "unread": getattr(mail_item, 'UnRead', False),
            "importance": getattr(mail_item, 'Importance', 1),
            "categories": getattr(mail_item, 'Categories', "")
        }
        return email_data
    except Exception as e:
        raise Exception(f"Failed to format email: {str(e)}")

def clear_email_cache():
    """Clear the email cache"""
    global email_cache
    email_cache = {}

def get_emails_from_folder(folder, days: int, search_term: Optional[str] = None):
    """Get emails from a folder with optional search filter"""
    emails_list = []
    
    # Calculate the date threshold
    now = datetime.datetime.now()
    threshold_date = now - datetime.timedelta(days=days)
    
    try:
        # Set up filtering
        folder_items = folder.Items
        folder_items.Sort("[ReceivedTime]", True)  # Sort by received time, newest first
        
        # If we have a search term, apply it
        if search_term:
            # Handle OR operators in search term
            search_terms = [term.strip() for term in search_term.split(" OR ")]
            
            # Try to create a filter for subject, sender name or body
            try:
                # Build SQL filter with OR conditions for each search term
                sql_conditions = []
                for term in search_terms:
                    sql_conditions.append(f"\"urn:schemas:httpmail:subject\" LIKE '%{term}%'")
                    sql_conditions.append(f"\"urn:schemas:httpmail:fromname\" LIKE '%{term}%'")
                    sql_conditions.append(f"\"urn:schemas:httpmail:textdescription\" LIKE '%{term}%'")
                
                filter_term = f"@SQL=" + " OR ".join(sql_conditions)
                folder_items = folder_items.Restrict(filter_term)
            except:
                # If filtering fails, we'll do manual filtering later
                pass
        
        # Process emails
        count = 0
        for item in folder_items:
            try:
                if hasattr(item, 'ReceivedTime') and item.ReceivedTime:
                    # Convert to naive datetime for comparison
                    received_time = item.ReceivedTime.replace(tzinfo=None)
                    
                    # Skip emails older than our threshold
                    if received_time < threshold_date:
                        continue
                    
                    # Manual search filter if needed
                    if search_term and folder_items == folder.Items:  # If we didn't apply filter earlier
                        # Handle OR operators in search term for manual filtering
                        search_terms = [term.strip().lower() for term in search_term.split(" OR ")]
                        
                        # Check if any of the search terms match
                        found_match = False
                        for term in search_terms:
                            if (term in item.Subject.lower() or 
                                term in item.SenderName.lower() or 
                                term in item.Body.lower()):
                                found_match = True
                                break
                        
                        if not found_match:
                            continue
                    
                    # Format and add the email
                    email_data = format_email(item)
                    emails_list.append(email_data)
                    count += 1
            except Exception as e:
                print(f"Warning: Error processing email: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error retrieving emails: {str(e)}")
        
    return emails_list

# MCP Tools
@mcp.tool()
def mark_email_as_read( email_number: int) -> str:
    import traceback
    try:
        # Try cache first
        if email_number in email_cache:
            email_data = email_cache[email_number]
            entry_id = email_data.get("id")
        else:
            # Not in cache: fetch the Nth most recent email from Inbox
            _, namespace = connect_to_outlook()
            inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox
            items = inbox.Items
            items.Sort("[ReceivedTime]", True)  # Newest first

            # Get the Nth item (1-based index)
            count = 0
            entry_id = None
            for item in items:
                if hasattr(item, 'EntryID'):
                    count += 1
                    if count == email_number:
                        entry_id = item.EntryID
                        break

            if not entry_id:
                return f"Email #{email_number} not found in cache or inbox."

        # Now get the mail item by EntryID
        _, namespace = connect_to_outlook()
        mail_item = namespace.GetItemFromID(entry_id)
        if not mail_item:
            return f"Email #{email_number} could not be retrieved from Outlook."

        mail_item.UnRead = False  # Mark as read
        mail_item.Save()  # Save the change
        return f"Email #{email_number} has been marked as read."
    except Exception as e:
        tb = traceback.format_exc()
        return f"Failed to mark email as read: {str(e)}\nTraceback:\n{tb}"

@mcp.tool()
def list_folders() -> str:
    """
    List all available mail folders in Outlook
    
    Returns:
        A list of available mail folders
    """
    try:
        # Connect to Outlook
        _, namespace = connect_to_outlook()
        
        result = "Available mail folders:\n\n"
        
        # List all root folders and their subfolders
        for folder in namespace.Folders:
            result += f"- {folder.Name}\n"
            
            # List subfolders
            for subfolder in folder.Folders:
                result += f"  - {subfolder.Name}\n"
                
                # List subfolders (one more level)
                try:
                    for subsubfolder in subfolder.Folders:
                        result += f"    - {subsubfolder.Name}\n"
                except:
                    pass
        
        return result
    except Exception as e:
        return f"Error listing mail folders: {str(e)}"

@mcp.tool()
def list_recent_emails(days: int = 7, folder_name: Optional[str] = None) -> str:
    """
    List email titles from the specified number of days
    
    Args:
        days: Number of days to look back for emails (max 30)
        folder_name: Name of the folder to check (if not specified, checks the Inbox)
        
    Returns:
        Numbered list of email titles with sender information
    """
    if not isinstance(days, int) or days < 1 or days > MAX_DAYS:
        return f"Error: 'days' must be an integer between 1 and {MAX_DAYS}"
    
    try:
        # Connect to Outlook
        _, namespace = connect_to_outlook()
        
        # Get the appropriate folder
        if folder_name:
            folder = get_folder_by_name(namespace, folder_name)
            if not folder:
                return f"Error: Folder '{folder_name}' not found"
        else:
            folder = namespace.GetDefaultFolder(6)  # Default inbox
        
        # Clear previous cache
        clear_email_cache()
        
        # Get emails from folder
        emails = get_emails_from_folder(folder, days)
        
        # Format the output and cache emails
        folder_display = f"'{folder_name}'" if folder_name else "Inbox"
        if not emails:
            return f"No emails found in {folder_display} from the last {days} days."
        
        result = f"Found {len(emails)} emails in {folder_display} from the last {days} days:\n\n"
        
        # Cache emails and build result
        for i, email in enumerate(emails, 1):
            # Store in cache
            email_cache[i] = email
            
            # Format for display
            result += f"Email #{i}\n"
            result += f"Subject: {email['subject']}\n"
            result += f"From: {email['sender']} <{email['sender_email']}>\n"
            result += f"Received: {email['received_time']}\n"
            result += f"Read Status: {'Read' if not email['unread'] else 'Unread'}\n"
            result += f"Has Attachments: {'Yes' if email['has_attachments'] else 'No'}\n\n"
        
        result += "To view the full content of an email, use the get_email_by_number tool with the email number."
        return result
    
    except Exception as e:
        return f"Error retrieving email titles: {str(e)}"

@mcp.tool()
def search_emails(search_term: str, days: int = 7, folder_name: Optional[str] = None) -> str:
    """
    Search emails by contact name or keyword within a time period
    
    Args:
        search_term: Name or keyword to search for
        days: Number of days to look back (max 30)
        folder_name: Name of the folder to search (if not specified, searches the Inbox)
        
    Returns:
        Numbered list of matching email titles
    """
    if not search_term:
        return "Error: Please provide a search term"
        
    if not isinstance(days, int) or days < 1 or days > MAX_DAYS:
        return f"Error: 'days' must be an integer between 1 and {MAX_DAYS}"
    
    try:
        # Connect to Outlook
        _, namespace = connect_to_outlook()
        
        # Get the appropriate folder
        if folder_name:
            folder = get_folder_by_name(namespace, folder_name)
            if not folder:
                return f"Error: Folder '{folder_name}' not found"
        else:
            folder = namespace.GetDefaultFolder(6)  # Default inbox
        
        # Clear previous cache
        clear_email_cache()
        
        # Get emails matching search term
        emails = get_emails_from_folder(folder, days, search_term)
        
        # Format the output and cache emails
        folder_display = f"'{folder_name}'" if folder_name else "Inbox"
        if not emails:
            return f"No emails matching '{search_term}' found in {folder_display} from the last {days} days."
        
        result = f"Found {len(emails)} emails matching '{search_term}' in {folder_display} from the last {days} days:\n\n"
        
        # Cache emails and build result
        for i, email in enumerate(emails, 1):
            # Store in cache
            email_cache[i] = email
            
            # Format for display
            result += f"Email #{i}\n"
            result += f"Subject: {email['subject']}\n"
            result += f"From: {email['sender']} <{email['sender_email']}>\n"
            result += f"Received: {email['received_time']}\n"
            result += f"Read Status: {'Read' if not email['unread'] else 'Unread'}\n"
            result += f"Has Attachments: {'Yes' if email['has_attachments'] else 'No'}\n\n"
        
        result += "To view the full content of an email, use the get_email_by_number tool with the email number."
        return result
    
    except Exception as e:
        return f"Error searching emails: {str(e)}"

@mcp.tool()
def get_email_by_number(email_number: int) -> str:
    """
    Get detailed content of a specific email by its number from the last listing
    
    Args:
        email_number: The number of the email from the list results
        
    Returns:
        Full details of the specified email
    """
    try:
        if not email_cache:
            return "Error: No emails have been listed yet. Please use list_recent_emails or search_emails first."
        
        if email_number not in email_cache:
            return f"Error: Email #{email_number} not found in the current listing."
        
        email_data = email_cache[email_number]
        
        # Connect to Outlook to get the full email content
        _, namespace = connect_to_outlook()
        
        # Retrieve the specific email
        email = namespace.GetItemFromID(email_data["id"])
        if not email:
            return f"Error: Email #{email_number} could not be retrieved from Outlook."
        
        # Format the output
        result = f"Email #{email_number} Details:\n\n"
        result += f"Subject: {email_data['subject']}\n"
        result += f"From: {email_data['sender']} <{email_data['sender_email']}>\n"
        result += f"Received: {email_data['received_time']}\n"
        result += f"To: {', '.join(email_data['to'])}\n"
        result += f"CC: {', '.join(email_data['cc'])}\n"
        result += f"Has Attachments: {'Yes' if email_data['has_attachments'] else 'No'}\n"
        
        if email_data['has_attachments']:
            result += "Attachments:\n"
            for i in range(1, email.Attachments.Count + 1):
                attachment = email.Attachments(i)
                result += f"  - {attachment.FileName}\n"
        
        result += "\nBody:\n"
        result += email_data['body']
        
        result += "\n\nTo reply to this email, use the reply_to_email_by_number tool with this email number."
        
        return result
    
    except Exception as e:
        return f"Error retrieving email details: {str(e)}"

@mcp.tool()
def reply_to_email_by_number(email_number: int, reply_text: str) -> str:
    """
    Reply to a specific email by its number from the last listing
    
    Args:
        email_number: The number of the email from the list results
        reply_text: The text content for the reply
        
    Returns:
        Status message indicating success or failure
    """
    try:
        if not email_cache:
            return "Error: No emails have been listed yet. Please use list_recent_emails or search_emails first."
        
        if email_number not in email_cache:
            return f"Error: Email #{email_number} not found in the current listing."
        
        email_id = email_cache[email_number]["id"]
        
        # Connect to Outlook
        outlook, namespace = connect_to_outlook()
        
        # Retrieve the specific email
        email = namespace.GetItemFromID(email_id)
        if not email:
            return f"Error: Email #{email_number} could not be retrieved from Outlook."
        
        # Create reply
        reply = email.Reply()
        reply.Body = reply_text
        
        # Send the reply
        reply.Send()
        
        return f"Reply sent successfully to: {email.SenderName} <{email.SenderEmailAddress}>"
    
    except Exception as e:
        return f"Error replying to email: {str(e)}"

@mcp.tool()
def compose_email(recipient_email: str, subject: str, body: str, cc_email: Optional[str] = None) -> str:
    """
    Compose and send a new email
    
    Args:
        recipient_email: Email address of the recipient
        subject: Subject line of the email
        body: Main content of the email
        cc_email: Email address for CC (optional)
        
    Returns:
        Status message indicating success or failure
    """
    try:
        # Connect to Outlook
        outlook, _ = connect_to_outlook()
        
        # Create a new email
        mail = outlook.CreateItem(0)  # 0 is the value for a mail item
        mail.Subject = subject
        mail.To = recipient_email
        
        if cc_email:
            mail.CC = cc_email
        
        # Add signature to the body
        mail.Body = body
        
        # Send the email
        mail.Send()
        
        return f"Email sent successfully to: {recipient_email}"
    
    except Exception as e:
        return f"Error sending email: {str(e)}"


@mcp.tool()
def create_draft_reply_by_number(email_number: int, reply_text: str) -> str:
    """
    Create a draft reply to a specific email by its number from the last listing

    Args:
        email_number: The number of the email from the list results
        reply_text: The text content for the draft reply

    Returns:
        Status message with draft details
    """
    try:
        if not email_cache:
            return "Error: No cached emails. Use list_recent_emails/search first."

        email_data = email_cache.get(email_number)
        if not email_data:
            return f"Error: Email #{email_number} not found in cache."

        outlook, namespace = connect_to_outlook()
        email = namespace.GetItemFromID(email_data["id"])

        # Create draft reply
        reply = email.Reply()
        reply.Body = reply_text + "\n\n[AI-generated draft - review before sending]"
        reply.Save()  # Saves to Drafts folder

        return (f"Draft reply created successfully to email #{email_number}\n"
                f"Subject: {reply.Subject}\n"
                f"Draft ID: {reply.EntryID}\n"
                "Review in Outlook Drafts folder before sending.")

    except Exception as e:
        return f"Error creating draft reply: {str(e)}"


# Manual registry for Flask wrapper
tool_registry = {
    "list_folders": list_folders,
    "list_recent_emails": list_recent_emails,
    "search_emails": search_emails,
    "get_email_by_number": get_email_by_number,
    "reply_to_email_by_number": reply_to_email_by_number,
    "create_draft_reply_by_number":create_draft_reply_by_number,
    "get_emails_from_folder":get_emails_from_folder,
    "Compose and send a new email":compose_email,
    "mark_email_as_read":mark_email_as_read,
}


# Run the server
# Run the server
if __name__ == "__main__":  
    print("Starting Outlook MCP Server...")
    print("Connecting to Outlook...")
    
    try:
        # Test Outlook connection
        outlook, namespace = connect_to_outlook()
        inbox = namespace.GetDefaultFolder(6)  # 6 is inbox
        print(f"Successfully connected to Outlook. Inbox has {inbox.Items.Count} items.")
        
        # Run the MCP server
        print("Starting MCP server. Press Ctrl+C to stop.")
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
