const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.json());

// Change this to your Python API endpoint
const PYTHON_API_URL = "http://localhost:8000/ask";

async function MakeRequestToPythonServer(tool, args) {
  const payload = {
    tool,
    args: args,
  };

  const responce = await axios.post(PYTHON_API_URL, payload);

  return responce;
}

app.post("/ask", async (req, res) => {
  console.log("--the Request -->", req.body);

   let tool= req.body.tool?.toString();
    let args= req.body.args
    let responce; 

    

     switch (tool) {
    case "list_recent_emails":
      console.log("Tool name is  : ",tool)
       if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
      break;
    case "search_emails":
      console.log("Tool name is  : ",tool)
      console.log("args name is  : ",args)
      if(typeof args==='string'){
        args=JSON.parse(args);
       }
       try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
      break;
    case "get_email_by_number":
      console.log("Tool name is  : ",tool)
      console.log("args name is  : ",args)
      if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
      break;
    case"reply_to_email_by_number":
    if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
     break;
    case "create_draft_reply_by_number":
      if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
      break;
    case "get_emails_from_folder":
      console.log("Tool name is  : ",tool)
      console.log("args name is  : ",args)
      if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
      break;
    case "compose_email":
      console.log("Tool name is  : ",tool)
      console.log("args name is  : ",args)
      if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
     break;
      case "mark_email_as_read":
        console.log("Tool name is  : ",tool)
      console.log("args name is  : ",args)
      if(typeof args==='string'){
        args=JSON.parse(args);
       }
      try{
      responce= await MakeRequestToPythonServer(tool,args)
    //  console.log(responce.data)
       res.status(200).json(responce.data)

      }
      catch(e){
         res.status(400).json({
           error:"Python server request failed",
           info: e.message
         })
      }
        break;
    default:
      res.status(404).json({ error: "Tool not found" });
      break;
     }
 

  //   let parsedArgs = args;
  //    // If args is a string, try to parse it to an object
  //   if (typeof args === "string") {
  //   try {
  //     parsedArgs = JSON.parse(args);
  //     console.log("---------------> Days ",parsedArgs.days)
  //   } catch (e) {
  //     return res.status(400).json({
  //       error: "Invalid arguments: 'args' is not valid JSON.",
  //     });
  //   }
  // }
  // // Validate days parameter
  // const convertedToNumberDays = Number(parsedArgs.days);
  // if (
  //   typeof parsedArgs === "object" &&
  //   parsedArgs !== null &&
  //   !isNaN(convertedToNumberDays)
  // ) {
  //   parsedArgs.days = convertedToNumberDays; // Overwrite with valid number
  //   try {
  //      const response = await MakeRequestToPythonServer(tool, args);
  //     res.status(200).json(response.data);
  //     // console.log(" the responce......",response)
  //   } catch (error) {
  //     console.log("---------->", error);
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {
  //   res.status(400).json({
  //     error: "Invalid arguments: 'days' must be a valid number.",
  //   });
  // }
  // break;
  //   case "search_emails":
  //     const convertedDays = Number(args.days);

  //     if (
  //       typeof args === "object" &&
  //       args !== null &&
  //       typeof args.search_term === "string" &&
  //       args.search_term.trim() !== "" &&
  //       !isNaN(convertedDays)
  //     ) {
  //       args.days = convertedDays; // Ensure 'days' is a number

  //       try {
  //         const response = await MakeRequestToPythonServer(tool, args);
  //         res.status(200).json(response.data);
  //       } catch (error) {
  //         console.log("---------->", error )
  //         res.status(500).json({
  //           error: "Python server request failed",
  //           details: error.message,
  //         });
  //       }
  //     } else {
  //       res.status(400).json({
  //         error:
  //           "Invalid arguments: 'search_term' must be a non-empty string and 'days' must be a valid number.",
  //       });
  //     }
  //     break;
  //   case "get_email_by_number":
  // let parsedArgs1= args;

  // try {
  //   console.log("inside the case ", parsedArgs1);
  //   if (typeof parsedArgs1 === "string") {
  //     parsedArgs1 = JSON.parse(parsedArgs1);
  //     console.log("the args now is like this  ", parsedArgs1);
  //   }
  // } catch (parseError) {
  //   return res.status(400).json({
  //     error: "Invalid JSON format in arguments.",
  //     details: parseError.message,
  //   });
  // }

  // const emailNumber = Number(parsedArgs1.email_number);

  // if (
  //   typeof parsedArgs1 === "object" &&
  //   parsedArgs1 !== null &&
  //   Number.isInteger(emailNumber) &&
  //   emailNumber > 0
  // ) {
  //   parsedArgs1.email_number = emailNumber;

  //   console.log("the args now is like this in IF ", parsedArgs1);

  //   try {
  //     console.log("the args now is like this before calling ", parsedArgs1);
  //     const response = await MakeRequestToPythonServer(tool, parsedArgs1);
  //     res.status(200).json(response.data);
  //   } catch (error) {
  //     console.log("----------> the catch ", error);
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {
  //   console.log("the args now is like this in failure ", parsedArgs);
  //   res.status(400).json({
  //     error: "Invalid arguments: 'email_number' must be a positive integer.",
  //   });
  // }
  // break;
  //   case "reply_to_email_by_number":
  // const emailNum = Number(args.email_number);

  // if (
  //   typeof args === "object" &&
  //   args !== null &&
  //   Number.isInteger(emailNum) &&
  //   emailNum > 0 &&
  //   typeof args.reply_text === "string" &&
  //   args.reply_text.trim() !== ""
  // ) {
  //   args.email_number = emailNum; // ensure integer

  //   try {
  //     const response = await MakeRequestToPythonServer(tool, args);
  //     res.status(200).json(response.data);
  //   } catch (error) {
  //     console.log("---------->", error )
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {
  //   res.status(400).json({
  //     error:
  //       "Invalid arguments: 'email_number' must be a positive integer and 'reply_text' must be a non-empty string.",
  //   });
  // }
  // break;
  //   case "create_draft_reply_by_number":
  // const draftEmailNum = Number(args.email_number);

  // if (
  //   typeof args === "object" &&
  //   args !== null &&
  //   Number.isInteger(draftEmailNum) &&
  //   draftEmailNum > 0 &&
  //   typeof args.reply_text === "string" &&
  //   args.reply_text.trim() !== ""
  // ) {
  //   args.email_number = draftEmailNum;

  //   try {
  //     const response = await MakeRequestToPythonServer(tool, args);
  //     res.status(200).json(response.data);
  //   } catch (error) {
  //     console.log("---------->", error )
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {
  //   res.status(400).json({
  //     error:
  //       "Invalid arguments: 'email_number' must be a positive integer and 'reply_text' must be a non-empty string.",
  //   });
  // }
  // break;
  //   case "get_emails_from_folder":
  // if (
  //   typeof args === "object" &&
  //   args !== null &&
  //   typeof args.folder_name === "string" &&
  //   args.folder_name.trim() !== "" &&
  //   typeof args.days === "number" && 
  //   !isNaN(args.days) &&
  //   (typeof args.search_term === "undefined" || typeof args.search_term === "string")
  // ) {
  //   try {
  //     const response = await MakeRequestToPythonServer(tool, args);
  //     res.status(200).json(response.data);
  //   } catch (error) {
  //     console.log("------------> the error ",error)
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {

  //   res.status(400).json({
  //     error: "Invalid arguments: 'folder_name' must be a non-empty string, 'days' must be a number, and 'search_term' must be a string if provided.",
  //   });
  // }
  // break;
  //   case "compose_email":
  // if (
  //   typeof args === "object" &&
  //   args !== null &&
  //   typeof args.to === "string" &&
  //   args.to.trim() !== "" &&
  //   typeof args.subject === "string" &&
  //   args.subject.trim() !== "" &&
  //   typeof args.body === "string" &&
  //   args.body.trim() !== ""
  // ) {
  //   try {
  //     const response = await MakeRequestToPythonServer(tool, args);
  //     res.status(200).json(response.data);
  //   } catch (error) {
  //     console.log("---------->", error )
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {
  //   res.status(400).json({
  //     error:
  //       "Invalid arguments: 'to', 'subject', and 'body' must be non-empty strings.",
  //   });
  // }
  // break;
  //   case "mark_email_as_read":
  // const markEmailNum = Number(args.email_number);

  // if (
  //   typeof args === "object" &&
  //   args !== null &&
  //   Number.isInteger(markEmailNum) &&
  //   markEmailNum > 0
  // ) {
  //   args.email_number = markEmailNum;

  //   try {
  //     const response = await MakeRequestToPythonServer(tool, args);
  //     res.status(200).json(response.data);
  //   } catch (error) {
  //     console.log("---------->", error )
  //     res.status(500).json({
  //       error: "Python server request failed",
  //       details: error.message,
  //     });
  //   }
  // } else {
  //   res.status(400).json({
  //     error: "Invalid arguments: 'email_number' must be a positive integer.",
  //   });
  // }
  // break;
  //   default:
  //     res.status(404).json({ error: "Tool not found" });
  //     break;
  // }

});

app.use((req, res) => {
  res.status(404).json({ error: "Wrong Route" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Node Express server running on port ${PORT}`);
});

// API ENDPOINT:
// POST http://localhost:3000/ask
// Headers: Content-Type: application/json

// REQUEST FORMAT:
// {
//   "tool": "<tool_name>",
//   "args": { ... }
// }

// AVAILABLE TOOLS:

// 1. list_recent_emails
// - Lists emails from last N days
// - Arguments: days (number)
// - Example (last 3 days):
// {
//   "tool": "list_recent_emails",
//   "args": { "days": 3 }
// }

// 2. search_emails
// - Search emails by keyword
// - Arguments: search_term (string), days (number)
// - Example (search "invoice" last 7 days):
// {
//   "tool": "search_emails",
//   "args": { "search_term": "invoice", "days": 7 }
// }

// 3. get_email_by_number
// - Get full email details by ID
// - Arguments: email_number (integer)
// - Example (email #2):
// {
//   "tool": "get_email_by_number",
//   "args": { "email_number": 2 }
// }

// 3. reply_to_email_by_number
// - Reply to email by ID
// - Arguments: email_number (integer), reply_text (string)
// - Example (reply to email #1):
// {
//   "tool": "reply_to_email_by_number",
//   "args": { "email_number": 1, "reply_text": "Thank you!" }
// }

// 4. create_draft_reply_by_number
// - Create draft reply
// - Arguments: email_number (integer), reply_text (string)
// - Example (draft reply to email #1):
// {
//   "tool": "create_draft_reply_by_number",
//   "args": { "email_number": 1, "reply_text": "I'll respond soon." }
// }

// 5. get_emails_from_folder
// - Get emails from specific folder
// - Arguments: folder_name (string)
// - Example (from "Inbox"):
// {
//   "tool": "get_emails_from_folder",
//   "args": { "folder_name": "Inbox" }
// }

// 6. compose_email
// - Send new email
// - Arguments: to (string), subject (string), body (string)
// - Example:
// {
//   "tool": "compose_email",
//   "args": {
//     "to": "recipient@example.com",
//     "subject": "Meeting Reminder",
//     "body": "Reminder about our meeting tomorrow."
//   }
// }

// 7. mark_email_as_read
// - Mark email as read
// - Arguments: email_number (integer)
// - Example (mark email #3 as read):
// {
//   "tool": "mark_email_as_read",
//   "args": { "email_number": 3 }
// }
