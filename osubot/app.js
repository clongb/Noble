const Banchojs = require("bancho.js");
const nodesu = require('nodesu');
const { google } = require("googleapis");
const path = require('path');
const dotenv = require('dotenv').config( {
    path: path.join(__dirname, '.env')
} );

const serviceAccountKeyFile = `${process.env.SERVICE_ACCT_FILE}`;
const sheetId = `${process.env.GOOGLE_SHEET_ID}`;
const mapRange = "C4:O";

const config = require('./config.json');
const matchdb = require('../matchdb.json');
const api = new nodesu.Client(config.apiKey);

let mapOrder = [matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].map1, 
matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].map2, 
matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].map3, 
matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].map4, 
matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].map5];
let mapIndex = 0;
let mapsPlayed = 0;

const client = new Banchojs.BanchoClient(config);

const prefix = ".";

async function _getGoogleSheetClient() {
  const auth = new google.auth.GoogleAuth({
    keyFile: serviceAccountKeyFile,
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });
  const authClient = await auth.getClient();
  return google.sheets({
    version: 'v4',
    auth: authClient,
  });
}

async function _readGoogleSheet(googleSheetClient, sheetId, tabName, range) {
  const res = await googleSheetClient.spreadsheets.values.get({
    spreadsheetId: sheetId,
    range: `${tabName}!${range}`,
  });

  return res.data.values;
}

async function startOsuBot() {
    let poolTab = "testpool";

    try {
        await client.connect();
        console.log("osu!bot Connected...")
        channel = await client.createLobby("OCW: Lobby test");
    } catch (err) {
        console.error(err);
        console.log("Failed to create lobby");
        process.exit(1);
    }

    lobby = channel.lobby;
    
    const password = Math.random().toString(36).substring(8);
    await lobby.setPassword(password);
    console.log("Lobby created!");
    console.log(`Name: ${lobby.name}, password: ${password}`);
    console.log(`Multiplayer link: https://osu.ppy.sh/mp/${lobby.id}`);
    
    lobby.setSettings(Banchojs.BanchoLobbyTeamModes.HeadToHead, Banchojs.BanchoLobbyWinConditions.ScoreV2, 10);
    setBeatmap(mapOrder[mapsPlayed], poolTab);
    await lobby.invitePlayer(matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].player);
    createListeners(mappool, lobby.id);   
}

async function setBeatmap(slot, matchId) {
    const googleSheetClient = await _getGoogleSheetClient();
    const mappool = await _readGoogleSheet(googleSheetClient, sheetId, matchId, mapRange);
    let rowIndex = 0;

    for (let i = 0; i < mappool.length; i++) {
      if (mappool[i][0] === slot) {
        rowIndex = i;
        break;
      }
    }

    let name = mappool[rowIndex][1];
    let mapId = mappool[rowIndex][12];
    console.log("Map info received");
    
    console.log(`Selecting map ${+mapsPlayed+1}: ${name}`);
    channel.sendMessage(`Selecting map ${+mapsPlayed+1}: ${name}`);
    let mod = slot.slice(0, 2);
    if (mod.includes("NM")) {
      mod = "";
    }
    mod = mod + " NF";
    lobby.setMap(mapId);
    lobby.setMods(mod, false);
}

async function compareObjects(mp, mappool, mapIndex, mapsPlayed){
    const multi = await api.multi.getMatch(mp);
    const scoreJson = multi.games[mapIndex].scores;
    let objectSum = +scoreJson[0].count50 + +scoreJson[0].count100 + +scoreJson[0].count300 + +scoreJson[0].countmiss;
    let totalObjects = mappool[mapsPlayed][11];
    let difference = objectSum / totalObjects;
    return difference;
}

function createListeners(mappool, mp) {
    lobby.on("playerJoined", (obj) => {
        const name = obj.player.user.username;
        console.log(`Player ${name} has joined!`);

        if (obj.player.user.isClient()) {
            lobby.setHost("#" + obj.player.user.id);
        }
    });

    lobby.on("allPlayersReady", (obj) => {
        console.log("All players are ready, starting match...");
        channel.sendMessage("All players are ready, starting match in 10 seconds!");
        channel.sendMessage("Type .abort if you would like to abort the timer.");
        lobby.startMatch(10);
     });

    lobby.on("matchFinished", async () => {
        mapIndex++;
        compareObjects(mp, mappool, (mapIndex-1), mapsPlayed).then((value) => {
          if (value < 0.80) {
            console.log("Current map has been aborted.");
            channel.sendMessage("You've aborted the current map. Ready up and try again!");
          } else {
            mapsPlayed++;
            if (mapsPlayed <= 4) {
              channel.sendMessage("Map complete, score has been recorded!");
              setBeatmap(mapOrder[mapsPlayed], matchId);
            }
          } 
        });
        if (mapsPlayed > 4) {
          console.log("Closing lobby and disconnecting...");
          channel.sendMessage("Lobby has been completed! GGWP!");
	        await lobby.closeLobby();
	        await client.disconnect();
        }           
    });

    channel.on("message", async (msg) => {
      if (msg[0] !== ".") return;

      const command = msg.split(" ")[0].toLowerCase();

      switch(command) {
        case prefix + "abort":
          lobby.abortTimer();
          console.log("Timer has been aborted.");
          channel.sendMessage("Timer has been aborted.");
      }
    });

    client.on("PM", async({ msg, user }) => {
      if (user.ircUsername === USERNAME) return;

      if (msg[0] !== ".") return;

      const command = msg.split(" ")[0].toLowerCase();

      switch(command) {
        case prefix + "invite":
          if (user.ircUsername === matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].player) {
            console.log(`Inviting ${matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].player}`);
            await lobby.invitePlayer(matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]].player);
          }
      }
    }); 
}
startOsuBot("testpool");
