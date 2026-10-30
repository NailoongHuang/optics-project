import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const root='C:/Users/xuanm/Desktop/optics/presentations/midterm';
const file=process.argv[2]??'midterm-report-v2.pptx';
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/output/'+file));
await fs.mkdir(root+'/build/final-renders',{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(root+`/build/final-renders/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await b.arrayBuffer()));
}
console.log('Final exported PPTX reimported and rendered:',p.slides.items.length);
