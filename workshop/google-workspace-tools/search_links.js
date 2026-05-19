const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

const ACCOUNTS = {
  wescope: {
    label: 'WeScope',
    tokensPath: path.join('/Users/frankie/.openclaw/workspace', 'tokens.json'),
    clientSecretPath: path.join('/Users/frankie/.openclaw/workspace', 'client_secret.json'),
  },
  personal: {
    label: 'Personal',
    tokensPath: path.join('/Users/frankie/.openclaw/workspace', 'tokens_personal.json'),
    clientSecretPath: path.join('/Users/frankie/.openclaw/workspace', 'client_secret_personal.json'),
  },
};

async function searchGmail(accountKey, query) {
  const account = ACCOUNTS[accountKey];
  const tokens = JSON.parse(fs.readFileSync(account.tokensPath, 'utf8'));
  const creds = JSON.parse(fs.readFileSync(account.clientSecretPath, 'utf8'));
  const key = creds.installed || creds.web;
  
  const oAuth2Client = new google.auth.OAuth2(key.client_id, key.client_secret, key.redirect_uris[0]);
  oAuth2Client.setCredentials(tokens);
  
  const gmail = google.gmail({ version: 'v1', auth: oAuth2Client });
  
  try {
    const res = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: 50
    });

    console.log(`\n=== Gmail Results for ${account.label} ===`);
    const messages = res.data.messages || [];
    
    if (messages.length === 0) {
      console.log('No emails found.');
      return;
    }

    for (const msg of messages) {
      const msgData = await gmail.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'full',
      });
      
      const payload = msgData.data.payload;
      const headers = payload.headers;
      const subject = headers.find(h => h.name === 'Subject')?.value || '(No Subject)';
      const date = headers.find(h => h.name === 'Date')?.value || '(Unknown Date)';
      const from = headers.find(h => h.name === 'From')?.value || '(Unknown From)';
      const to = headers.find(h => h.name === 'To')?.value || '(Unknown To)';
      
      // Look for attachments
      const attachments = [];
      function extractAttachments(part) {
        if (part.filename && part.filename.length > 0) {
          attachments.push(part.filename);
        }
        if (part.parts) {
          part.parts.forEach(extractAttachments);
        }
      }
      extractAttachments(payload);
      
      console.log(`- Date: ${date}\n  From: ${from}\n  To: ${to}\n  Subject: ${subject}`);
      console.log(`  Snippet: ${msgData.data.snippet}`);
      if (attachments.length > 0) {
        console.log(`  Attachments: ${attachments.join(', ')}`);
      }
      console.log(`  MsgLink: https://mail.google.com/mail/u/0/#all/${msg.id}\n`);
    }

  } catch (err) {
    console.error(`Error searching ${account.label} Gmail:`, err.message);
  }
}

async function main() {
  const query = 'llaurent@laurenell.com has:attachment (nanny OR manager OR responsibilities OR duties OR gemma OR jemma OR guidelines) before:2025/01/01';
  console.log(`Searching Gmail for: ${query}`);
  await searchGmail('wescope', query);
  await searchGmail('personal', query);
}

main().catch(console.error);
