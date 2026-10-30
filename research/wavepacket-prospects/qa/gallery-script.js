
const data=JSON.parse(document.getElementById('manifest').textContent);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let active=null,mode='summary';
document.getElementById('intro').textContent=data.intro;
document.getElementById('footer').textContent=data.footer;
const tabs=document.getElementById('tabs');
data.demos.forEach((d,i)=>{
 const b=document.createElement('button');b.className='tab';b.type='button';b.setAttribute('role','tab');b.id='tab-'+d.id;
 b.innerHTML=`<small>DEMO ${String(i+1).padStart(2,'0')} · ${esc(d.status)}</small><strong>${esc(d.shortTitle)}</strong>`;
 b.onclick=()=>select(d.id);tabs.append(b);
});
function select(id){
 active=data.demos.find(d=>d.id===id)||data.demos[0];mode='summary';
 document.querySelectorAll('.tab').forEach(b=>b.setAttribute('aria-selected',String(b.id==='tab-'+active.id)));
 history.replaceState(null,'','#'+active.id);render();
}
function render(){
 const d=active, sources=d.sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join(' · ');
 document.getElementById('main').setAttribute('aria-labelledby','tab-'+d.id);
 document.getElementById('main').innerHTML=`<article class="panel">
 <span class="tag">${esc(d.status)}</span><h2>${esc(d.title)}</h2><p class="verdict">${esc(d.verdict)}</p>
 <div class="context"><div><div class="label">作者留下的问题</div><p>${esc(d.question)}</p><p>${sources}</p></div>
 <div><div class="label">本轮最小测试</div><p>${esc(d.test)}</p></div></div>
 <div class="metrics">${d.metrics.map(m=>`<div class="metric"><strong>${esc(m.value)}</strong><span>${esc(m.label)}</span></div>`).join('')}</div>
 <div class="toolbar"><button class="mode" type="button" data-mode="summary" aria-pressed="${mode==='summary'}">结果图</button>
 <button class="mode" type="button" data-mode="animation" aria-pressed="${mode==='animation'}">播放动画</button></div>
 <figure class="figure"><img id="demo-image" src="${esc(mode==='animation'?d.animation:d.summary)}" alt="${esc(d.title)}">
 <figcaption>${esc(mode==='animation'?d.animationCaption:d.summaryCaption)}</figcaption></figure>
 <div class="scope"><strong>结论适用范围：</strong>${esc(d.scope)}</div>
 <div class="evidence"><div><div class="label">对照与核验</div><ul>${d.checks.map(s=>`<li>${esc(s)}</li>`).join('')}</ul></div>
 <div><div class="label">是否值得继续</div><p>${esc(d.next)}</p></div></div>
 <div class="files"><a href="${esc(d.results)}" target="_blank">原始结果 JSON</a><a href="${esc(d.report)}" target="_blank">该测试说明</a><a href="${esc(d.script)}" target="_blank">复现脚本</a></div>
 </article>`;
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;render()});
 document.getElementById('demo-image').onclick=()=>{document.getElementById('zoomimg').src=document.getElementById('demo-image').src;document.getElementById('zoom').showModal()};
}
document.getElementById('closezoom').onclick=()=>document.getElementById('zoom').close();
window.addEventListener('hashchange',()=>select(location.hash.slice(1)));
select(location.hash.slice(1));
