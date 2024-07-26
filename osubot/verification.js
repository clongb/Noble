const Banchojs = require("bancho.js");

const fs = require('fs');
const config = require('./config.json');
const code = require('../code.json')

const client = new Banchojs.BanchoClient(config);
let verified = 1;

async function startOsuBot() {
    try {
        await client.connect();
        
        client.on("PM", async (msg) => {
            if (msg.user.ircUsername === code.osu_username && msg.message === code.code) {
                verified = 0;
                await msg.user.sendMessage("Successfully linked your osu! account to discord!");
                disconnect();
            }
          }); 
    } catch (err) {
        console.error(err);
        process.exit(1);
    }

    setTimeout(disconnect, 60000);
}

function disconnect() { 
    client.disconnect();
    process.exit(verified);
}
startOsuBot();