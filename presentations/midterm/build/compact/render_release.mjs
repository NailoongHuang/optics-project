import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const work='C:/Users/xuanm/Desktop/optics/presentations/midterm';
const build=work+'/build/compact';
const meta=JSON.parse(await fs.readFile(build+'/build_result.json','utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(work+'/output/'+meta.release));
if(p.slides.items.length!==18)throw new Error('Wrong slide count');
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(build+`/final-renders/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await b.arrayBuffer()));
}
console.log('Reimported exported PPTX, rendered 18 slides');
