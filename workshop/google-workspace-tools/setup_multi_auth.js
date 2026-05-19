#!/usr/bin/env node
/**
 * setup_multi_auth.js — OAuth setup for multiple Google accounts
 *
 * Usage:
 *   node setup_multi_auth.js wescope     — Auth frankie@wescope.com
 *   node setup_multi_auth.js personal    — Auth frankie.soriano@gmail.com
 *   node setup_multi_auth.js exchange wescope <code>   — Exchange code for wescope
 *   node setup_multi_auth.js exchange personal <code>  — Exchange code for personal
 */

const { google } = require('googleapis');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// Account configurations — each account uses its own GCP project + client secret
const ACCOUNTS = {
  wescope: {
    label: 'frankie@wescope.com (WeScope)',
    tokensPath: path.join(__dirname, 'tokens.json'),
    clientSecretPath: path.join(__dirname, 'client_secret.json'),       // xano-fivetran-bq (Internal)
    loginHint: 'frankie@wescope.com',
  },
  personal: {
    label: 'frankie.soriano@gmail.com (Personal)',
    tokensPath: path.join(__dirname, 'tokens_personal.json'),
    clientSecretPath: path.join(__dirname, 'client_secret_personal.json'), // frankie-personal-tools (External)
    loginHint: 'frankie.soriano@gmail.com',
  },
};

// Full scope set — everything in GSuite
const SCOPES = [
  // Gmail
  'https://www.googleapis.com/auth/gmail.modify',
  'https://www.googleapis.com/auth/gmail.send',
  // Calendar
  'https://www.googleapis.com/auth/calendar',
  // Drive
  'https://www.googleapis.com/auth/drive',
  // Docs
  'https://www.googleapis.com/auth/documents',
  // Sheets
  'https://www.googleapis.com/auth/spreadsheets',
  // Slides
  'https://www.googleapis.com/auth/presentations',
  // Chat (read)
  'https://www.googleapis.com/auth/chat.spaces.readonly',
  'https://www.googleapis.com/auth/chat.memberships.readonly',
  'https://www.googleapis.com/auth/chat.messages.readonly',
  // Directory / People
  'https://www.googleapis.com/auth/directory.readonly',
  'https://www.googleapis.com/auth/contacts.readonly',
  // Profile
  'https://www.googleapis.com/auth/userinfo.profile',
  'https://www.googleapis.com/auth/userinfo.email',
  // Tasks
  'https://www.googleapis.com/auth/tasks',
];

function loadClientCredentials(clientSecretPath) {
  if (!fs.existsSync(clientSecretPath)) {
    console.error('❌ client_secret not found at', clientSecretPath);
    process.exit(1);
  }
  const content = fs.readFileSync(clientSecretPath, 'utf8');
  const keys = JSON.parse(content);
  const key = keys.installed || keys.web;
  return {
    clientId: key.client_id,
    clientSecret: key.client_secret,
    redirectUri: key.redirect_uris && key.redirect_uris.length > 0 ? key.redirect_uris[0] : 'http://localhost',
  };
}

function generateAuthUrl(accountKey) {
  const account = ACCOUNTS[accountKey];
  if (!account) {
    console.error(`❌ Unknown account: ${accountKey}. Use: wescope or personal`);
    process.exit(1);
  }

  const { clientId, clientSecret, redirectUri } = loadClientCredentials(account.clientSecretPath);
  const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent',  // Force consent to ensure we get a refresh_token
    login_hint: account.loginHint,
  });

  console.log(`\n🔑 Authorize ${account.label}`);
  console.log('━'.repeat(60));
  console.log('\n1. Open this URL in your browser:\n');
  console.log(authUrl);
  console.log('\n2. Sign in with:', account.loginHint);
  console.log('3. After authorization, you\'ll be redirected to localhost');
  console.log('4. Copy the "code" parameter from the URL');
  console.log('\n5. Run this to exchange the code:');
  console.log(`   node setup_multi_auth.js exchange ${accountKey} <paste_code_here>\n`);
}

async function exchangeCode(accountKey, code) {
  const account = ACCOUNTS[accountKey];
  if (!account) {
    console.error(`❌ Unknown account: ${accountKey}. Use: wescope or personal`);
    process.exit(1);
  }

  const { clientId, clientSecret, redirectUri } = loadClientCredentials(account.clientSecretPath);
  const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

  try {
    const { tokens } = await oAuth2Client.getToken(code);
    fs.writeFileSync(account.tokensPath, JSON.stringify(tokens, null, 2));
    console.log(`✅ Tokens saved for ${account.label}`);
    console.log(`   Path: ${account.tokensPath}`);
    console.log(`   Scopes: ${tokens.scope || 'not returned (normal)'}`);

    // Verify the token works
    oAuth2Client.setCredentials(tokens);
    const oauth2 = google.oauth2({ version: 'v2', auth: oAuth2Client });
    const userInfo = await oauth2.userinfo.get();
    console.log(`   Verified: ${userInfo.data.email}`);
  } catch (err) {
    console.error('❌ Error exchanging code:', err.message);
    if (err.message.includes('invalid_grant')) {
      console.log('\n💡 The code may have expired. Generate a new one:');
      console.log(`   node setup_multi_auth.js ${accountKey}`);
    }
  }
}

async function interactiveAuth(accountKey) {
  const account = ACCOUNTS[accountKey];
  if (!account) {
    console.error(`❌ Unknown account: ${accountKey}. Use: wescope or personal`);
    process.exit(1);
  }

  const { clientId, clientSecret, redirectUri } = loadClientCredentials(account.clientSecretPath);
  const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent',
    login_hint: account.loginHint,
  });

  console.log(`\n🔑 Authorize ${account.label}`);
  console.log('━'.repeat(60));
  console.log('\nOpen this URL in your browser:\n');
  console.log(authUrl);
  console.log();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  rl.question('Paste the code from the redirect URL: ', async (code) => {
    rl.close();
    await exchangeCode(accountKey, code.trim());
  });
}

// Status check
async function checkStatus() {
  console.log('\n📊 Google Workspace Auth Status');
  console.log('━'.repeat(60));

  for (const [key, account] of Object.entries(ACCOUNTS)) {
    process.stdout.write(`\n${account.label}: `);
    if (!fs.existsSync(account.tokensPath)) {
      console.log('❌ No tokens');
      continue;
    }

    try {
      const tokenData = JSON.parse(fs.readFileSync(account.tokensPath, 'utf8'));
      const { clientId, clientSecret, redirectUri } = loadClientCredentials(account.clientSecretPath);
      const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);
      oAuth2Client.setCredentials(tokenData);

      const oauth2 = google.oauth2({ version: 'v2', auth: oAuth2Client });
      const userInfo = await oauth2.userinfo.get();
      console.log(`✅ ${userInfo.data.email}`);

      // Show scope summary
      if (tokenData.scope) {
        const scopeNames = tokenData.scope.split(' ').map(s => s.split('/').pop());
        console.log(`   Scopes: ${scopeNames.join(', ')}`);
      }
    } catch (e) {
      console.log(`⚠️  Token exists but: ${e.message}`);
    }
  }
  console.log();
}

// ── CLI ─────────────────────────────────────────────────────────────────────

const cmd = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

if (!cmd || cmd === 'status') {
  checkStatus();
} else if (cmd === 'exchange') {
  if (!arg1 || !arg2) {
    console.log('Usage: node setup_multi_auth.js exchange <wescope|personal> <code>');
    process.exit(1);
  }
  exchangeCode(arg1, arg2);
} else if (ACCOUNTS[cmd]) {
  // Interactive auth
  interactiveAuth(cmd);
} else {
  console.log('Usage:');
  console.log('  node setup_multi_auth.js                       — Check auth status');
  console.log('  node setup_multi_auth.js wescope               — Auth wescope account');
  console.log('  node setup_multi_auth.js personal              — Auth personal account');
  console.log('  node setup_multi_auth.js exchange <account> <code> — Exchange auth code');
}
