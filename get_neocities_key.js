#!/usr/bin/env node
/**
 * Get Neocities API key using username/password via the neocities library.
 * Reads credentials from stdin prompts (password not echoed).
 * Saves the API key to ~/.neocities_api_key for reuse.
 */
const Neocities = require("neocities");
const fs = require("fs");
const path = require("path");
const readline = require("readline");

const API_KEY_FILE = path.join(require("os").homedir(), ".neocities_api_key");

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(q) {
    return new Promise((resolve) => {
        rl.question(q, resolve);
    });
}

(async () => {
    const username = await question("Neocities username (e.g. nolove): ");
    // Hide password input
    process.stdin.setRawMode(true);
    process.stdout.write("Neocities password: ");
    let password = "";
    await new Promise((resolve) => {
        process.stdin.once("data", (data) => {
            password = data.toString().trim();
            process.stdin.setRawMode(false);
            process.stdout.write("\n");
            resolve();
        });
    });

    console.log("\n🔑 Requesting API key from Neocities...");
    const api = new Neocities(username, password);

    api.key(function(resp) {
        if (resp.result === "success") {
            const apiKey = resp.api_key;
            fs.writeFileSync(API_KEY_FILE, apiKey);
            try { fs.chmodSync(API_KEY_FILE, 0o600); } catch(e) {}
            console.log(`✅ API key saved to ${API_KEY_FILE}`);
            console.log(`   (key value is not displayed for security)`);
            console.log(`\nYou can now use it in your script with:`);
            console.log(`  export NEOCITIES_USERNAME='${username}'`);
            console.log(`  export NEOCITIES_PASSWORD='<your-password>'`);
            console.log(`\nOr just set the cached key and run the sorter:`);
            console.log(`  python3 /home/scorn/neocities_sort.py --dry-run`);
        } else {
            console.log(`❌ Failed to get API key: ${JSON.stringify(resp)}`);
        }
        rl.close();
        process.exit(0);
    });
})();
