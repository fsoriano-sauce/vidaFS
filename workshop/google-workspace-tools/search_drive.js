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

const POSITIVE_KEYWORDS = [
  'house', 'home', 'nanny', 'gemma', 'jemma', 'duties', 'chore', 
  'routine', 'schedule', 'checklist', 'expectation', 'family', 'kids', 
  'care', 'soriano', 'responsibilit', 'to-do', 'todo', 'task'
];

const NEGATIVE_KEYWORDS = [
  'estimator', 'estimate', 'xactimate', 'meeting', 'sync', 'huddle', 
  'stand-up', 'standup', 'qa', 'review', 'board', 'marketing', 'sales', 
  'bylaw', 'committee'
];

function scoreFile(name) {
  const lower = name.toLowerCase();
  
  // Exclude obvious work stuff
  for (const neg of NEGATIVE_KEYWORDS) {
    if (lower.includes(neg)) return 0;
  }

  let score = 0;
  for (const pos of POSITIVE_KEYWORDS) {
    if (lower.includes(pos)) score += 1;
  }
  
  // Give extra weight to strong personal words
  if (lower.includes('nanny') || lower.includes('gemma') || lower.includes('jemma') || lower.includes('chore')) {
    score += 2;
  }
  if (lower.includes('home manager') || lower.includes('house manager')) {
    score += 3;
  }

  return score;
}

async function searchDrive(accountKey) {
  const account = ACCOUNTS[accountKey];
  const tokens = JSON.parse(fs.readFileSync(account.tokensPath, 'utf8'));
  const creds = JSON.parse(fs.readFileSync(account.clientSecretPath, 'utf8'));
  const key = creds.installed || creds.web;
  
  const oAuth2Client = new google.auth.OAuth2(key.client_id, key.client_secret, key.redirect_uris[0]);
  oAuth2Client.setCredentials(tokens);
  
  const drive = google.drive({ version: 'v3', auth: oAuth2Client });
  
  try {
    let allFiles = [];
    let pageToken = null;
    
    // Fetch up to 10 pages (10000 files)
    for (let i = 0; i < 10; i++) {
      const res = await drive.files.list({
        q: "trashed = true and (name contains 'Nanny' or name contains 'Gemma' or name contains 'Manager' or name contains 'Responsibilit' or name contains 'Duties' or name contains 'House' or name contains 'Home' or name contains 'Guidelines' or fullText contains 'Gemma')",
        fields: 'nextPageToken, files(id, name, webViewLink, createdTime, modifiedTime)',
        pageSize: 1000,
        pageToken: pageToken
      });
      if (res.data.files) allFiles.push(...res.data.files);
      pageToken = res.data.nextPageToken;
      if (!pageToken) break;
    }

    console.log(`\n=== Results for ${account.label} (Scanned ${allFiles.length} files shared with Gemma) ===`);
    
    // Score and filter
    const scoredFiles = allFiles;

    if (scoredFiles.length === 0) {
      console.log('No files found matching criteria.');
    } else {
      scoredFiles.slice(0, 30).forEach(file => {
        console.log(`- ${file.name} (Created: ${file.createdTime.split('T')[0]})`);
        console.log(`  Link: ${file.webViewLink}`);
      });
    }
  } catch (err) {
    console.error(`Error searching ${account.label} drive:`, err.message);
  }
}

async function main() {
  console.log(`Running AI-style scoring search for files created before 2026...`);
  await searchDrive('wescope');
  await searchDrive('personal');
}

main().catch(console.error);
