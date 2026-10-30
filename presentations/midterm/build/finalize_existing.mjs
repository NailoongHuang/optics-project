import fs from 'node:fs/promises';
import {finalizePresentation} from 'file:///C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations/container_tools/artifact_tool_utils.mjs';
const r='C:/Users/xuanm/Desktop/optics/presentations/midterm';
const s='C:/Users/xuanm/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.11052/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const before=JSON.parse(await fs.readFile(r+'/build/build_result.json','utf8'));
const tables=[...new Set(before.tables)],charts=[...new Set(before.charts)];
const result=await finalizePresentation({workspaceDir:r,candidatePath:r+'/build/candidate.pptx',
 finalPath:r+'/output/中期报告_单磁子传播.pptx',
 pythonExecutable:'C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:s+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:s+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeChartOwnerSlides:charts,requiredNativeTableOwnerSlides:tables,
 fontPolicy:{basis:'design',families:['Microsoft YaHei','Cambria']},verifyArtifactToolImport:true,
 materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',
 receiptPath:r+'/build/中期报告_单磁子传播.pptx.validation.json'});
await fs.writeFile(r+'/build/build_result.json',JSON.stringify({slides:35,charts,tables,finalizer:result},null,2));
console.log('Final release written successfully');
