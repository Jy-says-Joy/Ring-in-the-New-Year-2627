import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root = path.resolve(import.meta.dirname,'..');
const read = p => fs.readFileSync(path.join(root,p),'utf8');
const guide = JSON.parse(read('public/guide.json'));
const updates = JSON.parse(read('public/updates.json'));
assert.equal(guide.days.length,4);
assert.deepEqual(guide.days.map(d=>d.date),['2026-12-31','2027-01-01','2027-01-02','2027-01-03']);
assert.ok(Number.isFinite(Date.parse(guide.updatedAt)));
assert.match(guide.updatedAt,/(Z|[+-]\d\d:\d\d)$/);
for(const event of guide.countdowns||[]){assert.ok(Number.isFinite(Date.parse(event.at)));assert.match(event.at,/(Z|[+-]\d\d:\d\d)$/);}
for(const quote of [...guide.flightQuotes,...guide.hotelQuotes]){assert.ok(Number.isFinite(Date.parse(quote.checkedAt)));assert.match(quote.checkedAt,/(Z|[+-]\d\d:\d\d)$/);}
for(const day of guide.days){assert.ok(day.route.length>=2);assert.match(day.color,/^#[a-f\d]{6}$/i);assert.ok(day.items.length);assert.ok(day.sleep);}
function walk(value){if(Array.isArray(value)){for(const v of value)walk(v);}else if(value&&typeof value==='object'){for(const v of Object.values(value))walk(v);}else if(typeof value==='string'&&value.startsWith('http')){assert.equal(new URL(value).protocol,'https:');}}
walk(guide);walk(updates);
assert.ok(Array.isArray(updates.items));
new vm.Script(read('public/app.js'));
const html=read('public/index.html');
assert.ok(!/<(?:script|link|img)[^>]+(?:src|href)=["']https?:/i.test(html),'No external runtime assets');
assert.ok(!/type=["']checkbox/i.test(html));
for(const match of read('public/app.js').matchAll(/\$\('([^']+)'\)/g)){assert.ok(html.includes(`id="${match[1]}"`),`Missing element ${match[1]}`);}
for(const name of ['index.html','style.css','app.js','guide.json','updates.json','icon.svg','_headers'])assert.ok(fs.existsSync(path.join(root,'public',name)));
assert.equal(Date.parse('2027-01-01T00:00:00+09:00'),Date.parse('2026-12-31T15:00:00Z'));
console.log('PASS: data, dates, timezone target, internal references, JavaScript syntax, and zero external runtime assets.');
