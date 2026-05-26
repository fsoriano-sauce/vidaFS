#!/usr/bin/env node
/**
 * open_in_google.js
 * Automatically uploads a local Office file (Excel, CSV, Word, PowerPoint) to 
 * Google Drive with auto-conversion, then opens it in the default browser.
 *
 * Usage:
 *   node open_in_google.js <filePath>
 */

const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Determine paths for WeScope credentials
const TOKENS_PATH = path.join('/Users/frankie/.openclaw/workspace', 'tokens.json');
const CLIENT_SECRET_PATH = path.join('/Users/frankie/.openclaw/workspace', 'client_secret.json');

// Mapping of file extensions to Google Apps target MIME types
const EXTENSION_MAP = {
  // Spreadsheets (Google Sheets)
  '.csv': { target: 'application/vnd.google-apps.spreadsheet', source: 'text/csv' },
  '.xlsx': { target: 'application/vnd.google-apps.spreadsheet', source: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
  '.xls': { target: 'application/vnd.google-apps.spreadsheet', source: 'application/vnd.ms-excel' },
  
  // Documents (Google Docs)
  '.docx': { target: 'application/vnd.google-apps.document', source: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
  '.doc': { target: 'application/vnd.google-apps.document', source: 'application/msword' },
  '.rtf': { target: 'application/vnd.google-apps.document', source: 'application/rtf' },
  
  // Presentations (Google Slides)
  '.pptx': { target: 'application/vnd.google-apps.presentation', source: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' },
  '.ppt': { target: 'application/vnd.google-apps.presentation', source: 'application/vnd.ms-powerpoint' }
};

async function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error('❌ Error: No file path provided.');
    console.error('Usage: node open_in_google.js <filePath>');
    process.exit(1);
  }

  if (!fs.existsSync(filePath)) {
    console.error(`❌ Error: File not found at ${filePath}`);
    process.exit(1);
  }

  const ext = path.extname(filePath).toLowerCase();
  const mapping = EXTENSION_MAP[ext];

  if (!mapping) {
    console.error(`❌ Error: Unsupported file extension: ${ext}`);
    process.exit(1);
  }

  console.log(`📂 Processing file: ${filePath}`);
  
  // Check credentials
  if (!fs.existsSync(TOKENS_PATH) || !fs.existsSync(CLIENT_SECRET_PATH)) {
    console.error('❌ Error: Missing Google credentials in openclaw workspace.');
    process.exit(1);
  }

  const tokens = JSON.parse(fs.readFileSync(TOKENS_PATH, 'utf8'));
  const creds = JSON.parse(fs.readFileSync(CLIENT_SECRET_PATH, 'utf8'));
  const key = creds.installed || creds.web;
  
  const oAuth2Client = new google.auth.OAuth2(key.client_id, key.client_secret, key.redirect_uris[0]);
  oAuth2Client.setCredentials(tokens);
  
  const drive = google.drive({ version: 'v3', auth: oAuth2Client });

  try {
    console.log(`☁️ Uploading to Google Drive and converting to Google Format...`);
    const fileMetadata = {
      name: path.basename(filePath, ext), // Strip ext for native Google file feel
      mimeType: mapping.target,
    };
    const media = {
      mimeType: mapping.source,
      body: fs.createReadStream(filePath),
    };

    const response = await drive.files.create({
      requestBody: fileMetadata,
      media: media,
      fields: 'id, name, mimeType, webViewLink',
    });

    const file = response.data;
    console.log(`✅ Uploaded Successfully!`);
    console.log(`📝 File Name: ${file.name}`);
    console.log(`🏷️ MIME Type: ${file.mimeType}`);
    console.log(`🔗 Link: ${file.webViewLink}`);
    
    console.log(`🌐 Opening in browser...`);
    execSync(`open "${file.webViewLink}"`);
  } catch (err) {
    console.error(`❌ Google Drive API Error:`, err.message);
    if (err.message.includes('invalid_grant')) {
      console.log('\n💡 The OAuth tokens have expired or been revoked.');
      console.log('Please refresh authorization by running:');
      console.log('  node /Users/frankie/Documents/GitHub/vidaFS/workshop/google-workspace-tools/setup_multi_auth.js wescope');
    }
    process.exit(1);
  }
}

main().catch(console.error);
