import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const p=Presentation.create({slideSize:{width:1280,height:720}});const s=p.slides.add();
const bytes=await fs.readFile('C:/Users/xuanm/Desktop/optics/figures/midterm-report/b-local-flip/b16-anisotropic-propagation.gif');
s.images.add({blob:bytes,contentType:'image/gif',fit:'contain',position:{left:40,top:40,width:1200,height:640},alt:'各向异性对照动画'});
await(await PresentationFile.exportPptx(p)).save('gif_probe.pptx');
const b=await p.export({slide:s,format:'png',scale:1});await fs.writeFile('gif_probe.png',new Uint8Array(await b.arrayBuffer()));
console.log('GIF probe complete, exitCode',process.exitCode);
