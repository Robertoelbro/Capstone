import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const ROOT='C:/Users/Roberto/Documents/GitHub/Capstone/Fase 2/Evidencias Proyecto/BranchIt';
const BUILD=ROOT+'/.vercel/presentation-build';
const SKILL='C:/Users/Roberto/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const source='C:/Users/Roberto/Downloads/Presentacion proyecto (1).pptx';
process.env.RUNTIME_NODE_MODULES='C:/Users/Roberto/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs').href);
await fs.mkdir(ROOT+'/docs/presentacion',{recursive:true});
const r=await finalizePresentation({
 workspaceDir:ROOT,candidatePath:BUILD+'/candidate.pptx',finalPath:ROOT+'/docs/presentacion/BranchIT_Avances_Proyecto.pptx',
 pythonExecutable:'C:/Users/Roberto/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','9144000,5143500','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:17,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'reference',families:['Proxima Nova','Calibri','Arial'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:BUILD+'/validation.json'
});
console.log(JSON.stringify(r));
