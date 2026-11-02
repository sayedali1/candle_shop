/* Bakes the body of a recipe's blob part into a small file, built at a higher detail than the page could afford on a phone.
   Use:  node tools/bake-blob.mjs recipes/09-poodle-pups.json assets/models/pups-body.bin 96
   Then put  "bake": "assets/models/pups-body.bin"  on the blob part. The page loads the file; if it cannot, it builds the body itself from "els". */
import { register } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const threeUrl = pathToFileURL(path.join(root, 'vendor/three/build/three.module.js')).href;
register('data:text/javascript,' + encodeURIComponent(`export async function resolve(s, c, n) { return s === 'three' ? { url: '${threeUrl}', shortCircuit: true } : n(s, c); }`));
const THREE = await import(threeUrl);
const { MarchingCubes } = await import(pathToFileURL(path.join(root, 'vendor/three/examples/jsm/objects/MarchingCubes.js')).href);
const { makeBlobGeometry, encodeBlob } = await import(pathToFileURL(path.join(root, 'blob-geometry.js')).href);
const [recipePath, out, res = '96'] = process.argv.slice(2);
const recipe = JSON.parse(readFileSync(recipePath, 'utf8'));
const part = recipe.parts.find(p => p.shape === 'blob' && p.bake === out) || recipe.parts.find(p => p.shape === 'blob');   // a recipe with several bodies: the one whose "bake" is this file
const t0 = Date.now();
const geo = makeBlobGeometry(THREE, MarchingCubes)({ ...part, res: +res });
const buf = encodeBlob(geo);
writeFileSync(out, Buffer.from(buf));
console.log(`res ${res}: ${geo.attributes.position.count} points, ${geo.index.count / 3} triangles, ${(buf.byteLength / 1024).toFixed(0)} KB, ${Date.now() - t0} ms -> ${out}`);
