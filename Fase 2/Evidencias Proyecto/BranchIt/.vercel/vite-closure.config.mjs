import base from '../frontend/vite.config.js';
import {fileURLToPath} from 'node:url';
export default {...base,root:fileURLToPath(new URL('../frontend/',import.meta.url)), server:{host:'127.0.0.1',port:5176,proxy:{'/qa-api':{target:'http://127.0.0.1:8003',changeOrigin:true,rewrite:path=>path.replace(/^\/qa-api/,'')}}}};
