const Banchojs = require("bancho.js");
const nodesu = require('nodesu');
const { google } = require("googleapis");
const fs = require('fs');

const serviceAccountKeyFile = `${process.env.SERVICE_ACCT_FILE}`;
const sheetId = `${process.env.GOOGLE_SHEET_ID}`;
const mapRange = "C4:O";

const config = require('./config.json');
const matchdb = require('../matchdb.json');
const api = new nodesu.Client(config.apiKey);

const date = new Date()
let utc = date.toUTCString()

let match = matchdb.matches[Object.keys(matchdb.matches)[Object.keys(matchdb.matches).length - 1]];
let mapOrder = [match.map1, match.map2, match.map3, match.map4, match.map5];
let scoreIndex = 0;
let rowIndex = 0;
let accIndex = 0;
let mapIndex = 0;
let mapsPlayed = 0;
let cellIncrement = 3;
let data = [[]];  

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

async function _writeGoogleSheet(googleSheetClient, sheetId, tabName, range, data) {
  await googleSheetClient.spreadsheets.values.append({
    spreadsheetId: sheetId,
    range: `${tabName}!${range}`,
    valueInputOption: "USER_ENTERED",
    insertDataOption: "OVERWRITE",
    resource: {
      "majorDimension": "ROWS",
      "values": data
    },
  })
}

function log(data) {
  fs.appendFile('./osubot/log.txt', data, (err) => {
    if (err) throw err;
  });
}

async function updateScores(googleSheetClient, sheetId, tabName, range, data) {
  await googleSheetClient.spreadsheets.values.update({
    spreadsheetId: sheetId,
    range: `${tabName}!${range}`,
    valueInputOption: "USER_ENTERED",
    resource: {
      "majorDimension": "ROWS",
      "values": data
    },
  })
}

async function startOsuBot() {
    let poolTab = "testpool";
    const googleSheetClient = await _getGoogleSheetClient();
    const mappool = await _readGoogleSheet(googleSheetClient, sheetId, poolTab, mapRange);

    try {
        await client.connect();
        setTimeout(log, 1000, "------------------------------------\n");
        setTimeout(log, 3000, "osu!bot Connected...\n");
        channel = await client.createLobby("OCW: Lobby test");
    } catch (err) {
        console.error(err);
        setTimeout(log, 3000, "Failed to create lobby\n");
        process.exit(1);
    }

    lobby = channel.lobby;
    
    const mpLink = `https://osu.ppy.sh/mp/${lobby.id}`
    const password = Math.random().toString(36).substring(8);
    await lobby.setPassword(password);
    setTimeout(log, 5000, "Lobby created!\n");
    setTimeout(log, 7000, `Name: ${lobby.name}, password: ${password}\n`);
    setTimeout(log, 9000, `Multiplayer link: <${mpLink}>\n`);
    
    data[0][0] = utc;
    data[0][1] = mpLink;
    data[0][2] = match.player;
    
    let j = 0;
    if (match.phase === "defender") {
      data[0][3] = match.defense_attempts;
      j = 5;
      scoreIndex = 6;
      accIndex = 7;

      for (let i = 0; i < mapOrder.length; i++) {
        data[0][j] = mapOrder[i];
        j += 3;
      }
    } else if (match.phase === "attacker") {
      data[0][3] = match.attack_attempts;
      data[0][5] = match.defender;
      scoreIndex = 7;
      accIndex = 8;
      cellIncrement = 2;
    }
    
    
    
    updateData(); 
    lobby.setSettings(Banchojs.BanchoLobbyTeamModes.HeadToHead, Banchojs.BanchoLobbyWinConditions.ScoreV2, 10);
    setBeatmap(mapOrder[mapsPlayed], poolTab);
    setTimeout(log, 15000, `Inviting player: ${match.player}\n`);
    await lobby.invitePlayer(match.player);
    createListeners(mappool, lobby.id, poolTab);   
}

async function setBeatmap(slot, poolTab) {
    const googleSheetClient = await _getGoogleSheetClient();
    const mappool = await _readGoogleSheet(googleSheetClient, sheetId, poolTab, mapRange);
    let rowIndex = 0;

    for (let i = 0; i < mappool.length; i++) {
      if (mappool[i][0] === slot) {
        rowIndex = i;
        break;
      }
    }

    let name = mappool[rowIndex][1];
    let mapId = mappool[rowIndex][12];
    setTimeout(log, 11000, "Map info received\n");
    
    setTimeout(log, 13000, `Selecting map ${+mapsPlayed+1}: ${name}\n`);
    channel.sendMessage(`Selecting map ${+mapsPlayed+1}: ${name}`);
    let mod = slot.slice(0, 2);
    if (mod.includes("NM")) {
      mod = "";
    }
    mod = mod + " NF";
    lobby.setMap(mapId);
    lobby.setMods(mod, false);
}

async function updateData(updatingScores) {
    let column = '';
    if (match.phase === "attacker") {
      column = 'R';
    } else if (match.phase === "defender") {
      column = 'U';
    }
    let range = `B3:${column}`;

    const googleSheetClient = await _getGoogleSheetClient();
    const sheet = await _readGoogleSheet(googleSheetClient, sheetId, match.phase, range);
 
    if(sheet != undefined && !updatingScores) {
      for (let i = 0; i < sheet.length; i++) {
          rowIndex++;
      }
    }

    if(!updatingScores) {
      _writeGoogleSheet(googleSheetClient, sheetId, match.phase, `B${+rowIndex+3}:${column}${+rowIndex+3}`, data);
    } else {
      updateScores(googleSheetClient, sheetId, match.phase, `B${+rowIndex+3}:${column}${+rowIndex+3}`, data);
    }
}

async function compareObjects(mp, mappool, mapIndex, mapsPlayed) {
    const multi = await api.multi.getMatch(mp);
    const scoreJson = multi.games[mapIndex].scores;
    let objectSum = 0;
    let totalObjects = 0;
    let difference = 0;
    let rowIndex = 0;

    for (let i = 0; i < mappool.length; i++) {
      if (mappool[i][0] === mapOrder[mapsPlayed]) {
        rowIndex = i;
        break;
      }
    }
    
    try {
      objectSum = +scoreJson[0].count50 + +scoreJson[0].count100 + +scoreJson[0].count300 + +scoreJson[0].countmiss;
      totalObjects = mappool[rowIndex][11];
      difference = objectSum / totalObjects;
    } catch (error) {
      console.error(error);
    }
    
    return difference;
}

async function getScoreData(mp, mapIndex) {
    const multi = await api.multi.getMatch(mp);
    const scoreJson = multi.games[mapIndex].scores;
    let objectSum = +scoreJson[0].count50 + +scoreJson[0].count100 + +scoreJson[0].count300 + +scoreJson[0].countmiss;
    let accuracy = 100*((+50*scoreJson[0].count50 + +100*scoreJson[0].count100 + +300*scoreJson[0].count300) / (300*objectSum));
    let roundedAcc = Math.round(accuracy * 100) / 100;
    let accString = `${roundedAcc.toString()}%`;
    let result = [scoreJson[0].score, accString];

    return result;
}

async function closeLobby() {
  await lobby.closeLobby();
  await client.disconnect();
  process.exit()
}

function createListeners(mappool, mp, poolTab) {
    lobby.on("playerJoined", (obj) => {
        const name = obj.player.user.username;
        log(`Player ${name} has joined!\n`);
        
        if (obj.player.user.isClient()) {
          lobby.setHost("#" + obj.player.user.id);
        } else if (name === match.player) {
          channel.sendMessage(`Welcome ${name}!`);
          channel.sendMessage(`You will be recording your clan ${match.phase} scores across 5 maps. As soon as you click ready for each map, the map will start in 10 seconds. If you would like to abort the timer, type '.abort'`);
          if (match.phase == "defender") {
            channel.sendMessage(`The map order is as follows: ${mapOrder[0]}, ${mapOrder[1]}, ${mapOrder[2]}, ${mapOrder[3]}, ${mapOrder[4]}.`);
          } else if (match.phase == "attacker") {
            channel.sendMessage(`The player you will be attacking is ${match.defender} of ${match.defender_clan}. Their scores to beat are:`);
            channel.sendMessage(`${mapOrder[0]}: ${match.map1_defense_score}, ${mapOrder[1]}: ${match.map2_defense_score}, ${mapOrder[2]}: ${match.map3_defense_score}, ${mapOrder[3]}: ${match.map4_defense_score}, ${mapOrder[4]}: ${match.map5_defense_score}.`)
          }
        }
    });

    lobby.on("allPlayersReady", (obj) => {
        log("All players are ready, starting match...\n");
        channel.sendMessage("All players are ready, starting match in 10 seconds!");
        channel.sendMessage("Type .abort if you would like to abort the timer.");
        lobby.startMatch(10);
     });

    lobby.on("matchFinished", async () => {
        const name = match.player;
        mapIndex++;

        compareObjects(mp, mappool, (mapIndex-1), mapsPlayed).then((value) => {
          if (value < 0.30) {
            log("Current map has been aborted.\n");
            channel.sendMessage("You've aborted the current map. Ready up and try again!");
          } else {
            mapsPlayed++;
            getScoreData(mp, (mapIndex-1)).then((value) => {
              data[0][scoreIndex] = value[0];
              data[0][accIndex] = value[1];
              updateData(true);
              scoreIndex += cellIncrement;
              accIndex += cellIncrement;
              log(`Player ${name} has finished map ${+mapsPlayed} (Score: ${value[0]}, ${value[1]})\n`);
            });

            if (mapsPlayed <= 4) {
              channel.sendMessage("Map complete, score has been recorded!");
              setBeatmap(mapOrder[mapsPlayed], poolTab);
            } else if (mapsPlayed > 4) {
                log("Closing lobby and disconnecting...\n");
                channel.sendMessage("Lobby has been completed! GGWP! Closing lobby in 10 seconds...");
                setTimeout(closeLobby, 10000);
            }           
          } 
        });
    });

    channel.on("message", async (msg) => {
      if (msg.message[0] !== ".") return;

      const command = msg.message.split(" ")[0].toLowerCase();

      switch(command) {
        case prefix + "abort":
          lobby.abortTimer();
          log("Timer has been aborted.\n");
          channel.sendMessage("Timer has been aborted.");
      }
    });

    client.on("PART", async () => {
      if(!Banchojs.isBanchoLobby(client)) {
        log("Lobby has been closed.\n");
        client.disconnect();
        process.exit()
      }
    });

    client.on("PM", async(msg) => {
      if (msg.user.ircUsername === USERNAME) return;

      if (msg.message[0] !== ".") return;

      const command = msg.message.split(" ")[0].toLowerCase();

      switch(command) {
        case prefix + "invite":
          if (msg.user.ircUsername === match.player) {
            log(`Inviting ${match.player}\n`);
            await lobby.invitePlayer(match.player);
          }
      }
    }); 
}
startOsuBot();
