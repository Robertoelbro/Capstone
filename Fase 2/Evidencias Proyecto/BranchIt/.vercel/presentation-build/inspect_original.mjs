import fs from 'node:fs/promises';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const dir=process.cwd();
console.log('Importing original');
const p=await PresentationFile.importPptx(await FileBlob.load('C:/Users/Roberto/Downloads/Presentacion proyecto (1).pptx'));
console.log('slides',p.slides.items.length,'frame',p.slides.items[0].frame);
const info=await p.inspect({select:'$.slides[*]',include:['id','index','layout','elements.id','elements.kind','elements.text','elements.position','elements.style','notes.text']});
await fs.writeFile(dir+'/original-inspect.ndjson',info.ndjson);
console.log('masters',p.masters.items.length,'layouts',p.layouts.items.length);
await fs.mkdir(dir+'/original',{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const blob=await p.slides.items[i].export({format:'png',scale:1});
 await fs.writeFile(`${dir}/original/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await blob.arrayBuffer()));
 console.log('rendered',i+1);
}
const m=await p.export({format:'webp',montage:true,scale:.4});
await fs.writeFile(dir+'/original-montage.webp',new Uint8Array(await m.arrayBuffer()));
await fs.writeFile(dir+'/original-proto.json',JSON.stringify(p.toProto()));
