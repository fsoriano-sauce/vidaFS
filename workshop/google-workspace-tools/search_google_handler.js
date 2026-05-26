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
      maxResults: 20
    });

    console.log(`\n=== Gmail Results for ${account.label} (Query: ${query}) ===`);
    const messages = res.data.messages || [];
    
    if (messages.length === 0) {
      console.log('No emails found.');
      return;
    }

    for (const msg of messages) {
      const msgData = await gmail.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'full'
      });
      
      const headers = msgData.data.payload.headers;
      const subject = headers.find(h => h.name.toLowerCase() === 'subject')?.value || '(No Subject)';
      const date = headers.find(h => h.name.toLowerCase() === 'date')?.value || '(Unknown Date)';
      const from = headers.find(h => h.name.toLowerCase() === 'from')?.value || '(Unknown From)';
      const snippet = msgData.data.snippet || '';
      
      console.log(`- Date: ${date}\n  From: ${from}\n  Subject: ${subject}`);
      console.log(`  Snippet: ${snippet}`);
      console.log(`  Link: https://mail.google.com/mail/u/0/#all/${msg.id}`);
      
      // Let's dump the message parts if there is an attachment or code block
      const parts = msgData.data.payload.parts || [];
      for (const part of parts) {
        if (part.filename && part.filename.includes('open_in_google')) {
          console.log(`  [Attachment]: ${part.filename} (ID: ${part.body.attachmentId})`);
        }
      }
      console.log();
    }

  } catch (err) {
    console.error(`Error searching ${account.label} Gmail:`, err.message);
  }
}

async function searchDrive(accountKey, query) {
  const account = ACCOUNTS[accountKey];
  const tokens = JSON.parse(fs.readFileSync(account.tokensPath, 'utf8'));
  const creds = JSON.parse(fs.readFileSync(account.clientSecretPath, 'utf8'));
  const key = creds.installed || creds.web;
  
  const oAuth2Client = new google.auth.OAuth2(key.client_id, key.client_secret, key.redirect_uris[0]);
  oAuth2Client.setCredentials(tokens);
  
  const drive = google.drive({ version: 'v3', auth: oAuth2Client });
  
  try {
    const res = await drive.files.list({
      q: `name contains '${query}' or fullText contains '${query}'`,
      fields: 'files(id, name, webViewLink, createdTime, modifiedTime)',
      pageSize: 20
    });

    console.log(`\n=== Drive Results for ${account.label} (Query: ${query}) ===`);
    const files = res.data.files || [];
    
    if (files.length === 0) {
      console.log('No files found.');
      return;
    }

    files.forEach(file => {
      console.log(`- ${file.name} (ID: ${file.id}, Modified: ${file.modifiedTime})`);
      console.log(`  Link: ${file.webViewLink}`);
    });
  } catch (err) {
    console.error(`Error searching ${account.label} Drive:`, err.message);
  }
}

async function main() {
  console.log('Searching for open_in_google across accounts...');
  await searchGmail('wescope', 'open_in_google');
  await searchGmail('personal', 'open_in_google');
  
  await searchDrive('wescope', 'open_in_google');
  await searchDrive('personal', 'open_in_google');
  
  console.log('\nSearching for GoogleSuiteHandler across accounts...');
  await searchGmail('wescope', 'GoogleSuiteHandler');
  await searchGmail('personal', 'GoogleSuiteHandler');
}

main().catch(console.error);
