// Adapted local routing wrapper SHA256 fe744eecf12b767481c56e2d7cc924b79cf496043f01228883cb14a624057ff4
// Stock checker unchanged; process-local read routing to the prepared config.
import fs from 'node:fs/promises';
import {resolve} from 'node:path';
const base='creative/reviews/p29-lower-front-sheath-observed-b-v1-coordination-v1';
const original=fs.readFile.bind(fs);const cfg=JSON.parse(await original(base+'/coordinator-config.json','utf8'));
fs.readFile=async function(path,...args){if(resolve(String(path))===resolve('tools/motorcycle-lab/catalog.json'))return JSON.stringify({assets:{[cfg.key]:cfg}});return original(path,...args);};
process.argv[2]=cfg.key;await import('../../../tools/check_motorcycle18_exports_v2.mjs');
