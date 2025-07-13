import datetime
import os
import win32com.client
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
import pythoncom
import traceback

# Initialize FastMCP server
mcp = FastMCP("outlook-assistant")

# Constants
MAX_DAYS = 30
email_cache = {}

def connect_to_outlook():
    try:
        pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        return outlook, namespace
    except Exception as e:
        raise Exception(f"Failed to connect to Outlook: {str(e)}")

def get_folder_by_name(namespace, folder_name: str):
    try:
        inbox = namespace.GetDefaultFolder(6)
        # Search Inbox subfolders
        for folder in inbox.Folders:
            if hasattr(folder, "Name") and folder.Name.lower() == folder_name.lower():
                return folder

        # Search all accounts and their folders
        for account in namespace.Folders:
            if hasattr(account, "Name") and account.Name.lower() == folder_name.lower():
                return account
            if not hasattr(account, "Folders"):
                continue
            for folder in account.Folders:
                if hasattr(folder, "Name") and folder.Name.lower() == folder_name.lower():
                    return folder
                if not hasattr(folder, "Folders"):
                    continue
                for subfolder in folder.Folders:
                    if hasattr(subfolder, "Name") and subfolder.Name.lower() == folder_name.lower():
                        return subfolder
        return None
    except Exception as e:
        raise Exception(f"Failed to access folder {folder_name}: {str(e)}")



def get_account_folder(namespace, account_name: str):
    for folder in namespace.Folders:
        if folder.Name.lower() == account_name.lower():
            return folder
    raise Exception(f"Account '{account_name}' not found")

def get_emails_from_folder(folder, days: int, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    filtered_emails = []

    try:
        items = folder.Items
        items.Sort("[ReceivedTime]", True)  # Sort descending
    except Exception as e:
        raise Exception(f"Failed to retrieve or sort items in folder: {str(e)}")

    for item in items:
        if hasattr(item, "ReceivedTime"):
            received_time = item.ReceivedTime
            try:
                # Convert to naive datetime for comparison
                received_time_naive = received_time.replace(tzinfo=None)
                if received_time_naive >= cutoff:
                    if search_term:
                        combined_text = f"{item.Subject} {item.Body}".lower()
                        if search_term.lower() not in combined_text:
                            continue
                    filtered_emails.append(format_email(item))
            except Exception as e:
                # Skip problematic items but log them
                print(f"Skipping email due to error: {e}")
    return filtered_emails



def format_email(mail_item) -> Dict[str, Any]:
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
                if recipient.Type == 1:
                    to_recipients.append(recipient_str)
                elif recipient.Type == 2:
                    cc_recipients.append(recipient_str)
        return {
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
    except Exception as e:
        raise Exception(f"Failed to format email: {str(e)}")

def clear_email_cache():
    global email_cache
    email_cache = {}

@mcp.tool()
def list_recent_emails(days: int = 7, folder_name: Optional[str] = None, account_name: Optional[str] = None) -> str:
    if not isinstance(days, int) or days < 1 or days > MAX_DAYS:
        return f"Error: 'days' must be an integer between 1 and {MAX_DAYS}"
    try:
        _, namespace = connect_to_outlook()
        if account_name:
            account_folder = get_account_folder(namespace, account_name)
            folder = account_folder
            if folder_name:
                # Search inside this account
                for f in account_folder.Folders:
                    if f.Name.lower() == folder_name.lower():
                        folder = f
                        break
                else:
                    return f"Error: Folder '{folder_name}' not found in account '{account_name}'"
        else:
            folder = namespace.GetDefaultFolder(6) if not folder_name else get_folder_by_name(namespace, folder_name)

        clear_email_cache()
        emails = get_emails_from_folder(folder, days)
        folder_display = f"'{folder.Name}'" if folder else "Inbox"
        if not emails:
            return f"No emails found in {folder_display} from the last {days} days."
        result = f"Found {len(emails)} emails in {folder_display} from the last {days} days:\n\n"
        for i, email in enumerate(emails, 1):
            email_cache[i] = email
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
def search_emails(
    search_term: str,days: int = 7,folder_name: Optional[str] = None,account_name: Optional[str] = None) -> str:
    if not search_term:
        return "Error: Please provide a search term."
    if not isinstance(days, int) or days < 1 or days > MAX_DAYS:
        return f"Error: 'days' must be an integer between 1 and {MAX_DAYS}."

    try:
        _, namespace = connect_to_outlook()

        # Get the account folder if account_name is specified
        if account_name:
            try:
                account_folder = get_account_folder(namespace, account_name)
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            account_folder = namespace

        # Locate folder (Inbox by default or specified)
        if folder_name:
            folder = get_folder_by_name(account_folder, folder_name)
            if not folder:
                return f"Error: Folder '{folder_name}' not found"
        else:
            folder = account_folder.GetDefaultFolder(6)  # Inbox

        clear_email_cache()
        emails = get_emails_from_folder(folder, days, search_term)

        folder_display = f"'{folder_name}'" if folder_name else "Inbox"
        account_display = f" in account '{account_name}'" if account_name else ""
        if not emails:
            return f"No emails matching '{search_term}' found in {folder_display}{account_display} from the last {days} days."

        result = f"Found {len(emails)} emails matching '{search_term}' in {folder_display}{account_display} from the last {days} days:\n\n"
        for i, email in enumerate(emails, 1):
            email_cache[i] = email
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
def get_email_by_number(email_number: int,**kwargs) -> str:
    try:
        if not email_cache:
            return "Error: No emails have been listed yet. Please use list_recent_emails or search_emails first."
        if email_number not in email_cache:
            return f"Error: Email #{email_number} not found in the current listing."

        email_data = email_cache[email_number]

        # Connect and get email by EntryID (works across accounts)
        _, namespace = connect_to_outlook()
        email = namespace.GetItemFromID(email_data["id"])

        if not email:
            return f"Error: Email #{email_number} could not be retrieved from Outlook."

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
def reply_to_email_by_number(email_number: int, reply_body: str) -> str:
    try:
        if not email_cache:
            return "Error: No emails have been listed yet. Please use list_recent_emails or search_emails first."
        if email_number not in email_cache:
            return f"Error: Email #{email_number} not found in the current listing."

        email_data = email_cache[email_number]
        _, namespace = connect_to_outlook()

        # Retrieve the original email using EntryID (cross-account safe)
        email = namespace.GetItemFromID(email_data["id"])
        if not email:
            return f"Error: Original email for #{email_number} could not be retrieved."

        # Create the reply
        reply = email.Reply()

        # Add the reply body before the original message
        reply.HTMLBody = f"<p>{reply_body}</p><br>" + reply.HTMLBody

        # Send the reply
        reply.Send()

        return f"Replied successfully to email #{email_number}."

    except Exception as e:
        return f"Error replying to email: {str(e)}"


@mcp.tool()
def compose_email(recipient_email: str, subject: str, body: str, cc_email: Optional[str] = None) -> str:
    try:
        outlook, _ = connect_to_outlook()
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.To = recipient_email
        if cc_email:
            mail.CC = cc_email
        mail.Body = body
        mail.Send()
        return f"Email sent successfully to: {recipient_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.tool()
def create_draft_reply_by_number(email_number: int, reply_text: str) -> str:
    try:
        if not email_cache:
            return "Error: No cached emails. Use list_recent_emails/search first."
        email_data = email_cache.get(email_number)
        if not email_data:
            return f"Error: Email #{email_number} not found in cache."
        outlook, namespace = connect_to_outlook()
        email = namespace.GetItemFromID(email_data["id"])
        reply = email.Reply()
        reply.Body = reply_text + "\n\n[AI-generated draft - review before sending]"
        reply.Save()
        return (f"Draft reply created successfully to email #{email_number}\n"
                f"Subject: {reply.Subject}\n"
                f"Draft ID: {reply.EntryID}\n"
                "Review in Outlook Drafts folder before sending.")
    except Exception as e:
        return f"Error creating draft reply: {str(e)}"

@mcp.tool()
def mark_email_as_read(email_number: int) -> str:
    try:
        if email_number in email_cache:
            email_data = email_cache[email_number]
            entry_id = email_data.get("id")
        else:
            _, namespace = connect_to_outlook()
            inbox = namespace.GetDefaultFolder(6)
            items = inbox.Items
            items.Sort("[ReceivedTime]", True)
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
        _, namespace = connect_to_outlook()
        mail_item = namespace.GetItemFromID(entry_id)
        if not mail_item:
            return f"Email #{email_number} could not be retrieved from Outlook."
        mail_item.UnRead = False
        mail_item.Save()
        return f"Email #{email_number} has been marked as read."
    except Exception as e:
        tb = traceback.format_exc()
        return f"Failed to mark email as read: {str(e)}\nTraceback:\n{tb}"

@mcp.tool()
def list_folders() -> str:
    try:
        _, namespace = connect_to_outlook()
        result = "📂 Outlook Folders by Account:\n\n"

        for account in namespace.Folders:
            result += f"🔸 Account: {account.Name}\n"
            for folder in account.Folders:
                result += f"  - {folder.Name}\n"
                for subfolder in folder.Folders:
                    result += f"    ▪ {subfolder.Name}\n"
            result += "\n"

        return result or "No folders found."
    except Exception as e:
        return f"Error listing folders: {str(e)}"


tool_registry = {
    "list_recent_emails": list_recent_emails,
    "search_emails": search_emails,
    "get_email_by_number": get_email_by_number,
    "reply_to_email_by_number": reply_to_email_by_number,
    "create_draft_reply_by_number": create_draft_reply_by_number,
    "compose_email": compose_email,
    "mark_email_as_read": mark_email_as_read,
    "list_folders": list_folders,
}


# Run server
if __name__ == "__main__":
    print("Starting Outlook MCP Server...")
    print("Connecting to Outlook...")
    try:
        outlook, namespace = connect_to_outlook()
        inbox = namespace.GetDefaultFolder(6)
        print(f"Successfully connected to Outlook. Inbox has {inbox.Items.Count} items.")
        print("Starting MCP server. Press Ctrl+C to stop.")
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
