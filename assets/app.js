const cards=[...document.querySelectorAll('.card')];
const q=document.getElementById('q'),sort=document.getElementById('sort');
function apply(){
 const term=(q.value||'').toLowerCase();
 const gens=[...document.querySelectorAll('input[data-genre]:checked')].map(e=>e.value);
 const st=[...document.querySelectorAll('input[data-status]:checked')].map(e=>e.value);
 const eng=[...document.querySelectorAll('input[data-engine]:checked')].map(e=>e.value);
 const min=parseFloat(document.getElementById('minrating').value||'0');
 let vis=cards.filter(c=>{
  const hay=(c.dataset.title+' '+c.dataset.dev).toLowerCase();
  if(term&&!hay.includes(term))return false;
  if(gens.length&&!gens.some(g=>c.dataset.genres.split('|').includes(g)))return false;
  if(st.length&&!st.includes(c.dataset.status))return false;
  if(eng.length&&!eng.includes(c.dataset.engine))return false;
  if(parseFloat(c.dataset.rating)<min)return false;
  return true;
 });
 if(sort.value==='rating')vis.sort((a,b)=>b.dataset.rating-a.dataset.rating);
 if(sort.value==='newest')vis.sort((a,b)=>b.dataset.updated.localeCompare(a.dataset.updated));
 if(sort.value==='title')vis.sort((a,b)=>a.dataset.title.localeCompare(b.dataset.title));
 const grid=document.getElementById('grid');vis.forEach(c=>grid.appendChild(c));
 cards.forEach(c=>c.style.display=vis.includes(c)?'':'none');
 document.getElementById('count').textContent=vis.length+(vis.length===1?' game':' games');
}
document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',apply));
const p=new URLSearchParams(location.search);if(p.get('tag')){const cb=document.querySelector('input[data-genre="'+p.get('tag')+'"]');if(cb){cb.checked=true;}}
if(p.get('q')){q.value=p.get('q');}
if(p.get('sort')&&[...sort.options].some(o=>o.value===p.get('sort'))){sort.value=p.get('sort');}
apply();
