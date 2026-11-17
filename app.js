import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';
const $=s=>document.querySelector(s), viewport=$('#viewport');
const scene=new THREE.Scene();scene.background=new THREE.Color('#e9e6dd');
const camera=new THREE.PerspectiveCamera(42,1,.05,500);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;viewport.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.075;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=3;controls.maxDistance=240;
scene.add(new THREE.HemisphereLight(0xfff8e9,0xa6b09d,2.1));
const sun=new THREE.DirectionalLight(0xffedcf,2.5);sun.position.set(3,22,14);sun.target.position.set(13,0,-3);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-28,right:28,top:20,bottom:-20,near:1,far:70});sun.shadow.bias=-.001;sun.shadow.normalBias=.035;scene.add(sun,sun.target);
const fill=new THREE.DirectionalLight(0xdbe9ff,1.1);fill.position.set(20,12,-18);scene.add(fill);
for(const x of [3,10,19,24,29]){const light=new THREE.PointLight(0xffdca6,12,9,1);light.position.set(x,2.9,-3.5);scene.add(light);}
let model,mode='exterior',walking=false,showLabels=false,transition=null,yaw=0,pitch=0,drag=null;
const keys=new Set(), reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const views={
exterior:{pos:[46,30,40],target:[13,0,-3],roof:true,facade:true,title:'Внешний вид',description:'Тёплый камень · дуб · панорамное остекление'},
cutaway:{pos:[37,30,30],target:[13,0,-3.8],roof:false,facade:false,title:'Пространство целиком',description:'Два зала, кухни и служебные помещения'},
plan:{pos:[13,49,-3.85],target:[13,0,-3.9],roof:false,facade:false,title:'Планировка',description:'Объёмная схема · помещения по исходному плану'},
lounge:{pos:[1.3,1.65,-3.8],target:[9,1.5,-3.6],roof:true,facade:true,title:'Кофейный зал',description:'С уровня глаз · свободное перемещение'},
dining:{pos:[15.2,1.65,-3.7],target:[24,1.5,-4.2],roof:true,facade:true,title:'Основной зал',description:'Общий стол · мягкие диваны · камерный свет'}
};
function visibility(prefix,visible){model?.traverse(o=>{if(o.name.startsWith(prefix+'__'))o.visible=visible;});}
function setToggle(id,value){$(id).setAttribute('aria-pressed',String(value));}
function setView(name,immediate=false){
 mode=name;const v=views[name];walking=['lounge','dining'].includes(name);document.body.classList.toggle('walk',walking);$('#walkcontrols').hidden=!walking;controls.enabled=!walking;controls.autoRotate=false;setToggle('#rotate',false);
 controls.maxPolarAngle=name==='plan'?Math.PI*.49:Math.PI*.49;
 visibility('Roof',v.roof);visibility('Facade',v.facade);setToggle('#roof',v.roof);setToggle('#facade',v.facade);
 const pos=new THREE.Vector3(...v.pos),target=new THREE.Vector3(...v.target);
 if(!walking)pos.sub(target).multiplyScalar(Math.max(1,1.2/camera.aspect)).add(target);
 if(immediate||walking||reduced){camera.position.copy(pos);controls.target.copy(target);camera.lookAt(target);transition=null;}else transition={start:performance.now(),from:camera.position.clone(),to:pos,fromTarget:controls.target.clone(),toTarget:target};
 if(walking){const dir=target.clone().sub(pos).normalize();yaw=Math.atan2(-dir.x,-dir.z);pitch=Math.asin(dir.y);camera.rotation.order='YXZ';camera.rotation.set(pitch,yaw,0);}
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));$('#viewnum').textContent=`0${Object.keys(views).indexOf(name)+1} / 05`;$('#viewtitle').textContent=v.title;$('#viewdescription').textContent=v.description;
 $('#hint').textContent=walking?'Тяните для осмотра · WASD / стрелки — движение · Esc — наружу':'Тяните, чтобы вращать · Колесо — масштаб · Правая кнопка — сдвиг';
}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));
for(const [id,prefix] of [['#roof','Roof'],['#facade','Facade']])$(id).onclick=()=>{const visible=$(id).getAttribute('aria-pressed')!=='true';visibility(prefix,visible);setToggle(id,visible);};
$('#rotate').onclick=()=>{if(walking)setView('exterior',true);controls.autoRotate=!controls.autoRotate;controls.autoRotateSpeed=.5;setToggle('#rotate',controls.autoRotate);};
$('#labels').onclick=()=>{showLabels=!showLabels;setToggle('#labels',showLabels);};
$('#about').onclick=()=>$('#details').showModal();$('#close').onclick=()=>$('#details').close();
const rooms=[['01 · Холл',29,1.2,1.7],['02 · Кухня',29,1.2,6],['03 · Санузел',26.9,1.4,3.7],['04 · Основной зал',20,1.2,3.5],['05 · Коридор',13.2,1.2,6.3],['06 · Кухня',10,1.2,6],['07 · Подсобная',6.7,1.2,6],['08 · Кофейный зал',3.5,1.2,3.6],['09 · Коридор',-.8,1.2,4.2],['10 · Подсобная',-3.5,1.2,5.6],['11 · Санузел',-.8,1.4,6.7]];
const labels=rooms.map(([text,x,y,z])=>{const el=document.createElement('div');el.className='room-label';el.textContent=text;el.hidden=true;$('#labelsLayer').appendChild(el);return {el,pos:new THREE.Vector3(x,y,-z)};});
new GLTFLoader().load('./model/terra-cafe.glb',gltf=>{model=gltf.scene;scene.add(model);model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;if(o.material?.transparent)o.castShadow=false;}});$('#loading').style.display='none';setView('exterior',true);window.cafeReady=true;},e=>{$('#progress').textContent=e.total?`${Math.round(e.loaded/e.total*100)}%`:`${(e.loaded/1e6).toFixed(1)} МБ`;},err=>{$('#loading').innerHTML='<strong>Не удалось загрузить 3D</strong><span>Обновите страницу или скачайте модель ниже.</span><a href="model/terra-cafe.glb">Скачать GLB ↓</a>';console.error(err);});
function resize(){const w=viewport.clientWidth,h=viewport.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();if(model)setView(mode,true);}addEventListener('resize',resize);resize();setView('exterior',true);
renderer.domElement.addEventListener('pointerdown',e=>{transition=null;if(walking){drag={x:e.clientX,y:e.clientY};renderer.domElement.setPointerCapture(e.pointerId);}});
renderer.domElement.addEventListener('pointermove',e=>{if(!walking||!drag)return;yaw-=(e.clientX-drag.x)*.004;pitch=THREE.MathUtils.clamp(pitch-(e.clientY-drag.y)*.004,-1.3,1.3);drag={x:e.clientX,y:e.clientY};camera.rotation.set(pitch,yaw,0);});
for(const event of ['pointerup','pointercancel'])renderer.domElement.addEventListener(event,()=>drag=null);
addEventListener('keydown',e=>{if($('#details').open)return;if(e.code==='Escape'){setView('exterior');return;}if(walking&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)){e.preventDefault();keys.add(e.code);}});addEventListener('keyup',e=>keys.delete(e.code));addEventListener('blur',()=>keys.clear());
const moveCodes={forward:'KeyW',back:'KeyS',left:'KeyA',right:'KeyD'};document.querySelectorAll('[data-move]').forEach(b=>{b.onpointerdown=e=>{keys.add(moveCodes[b.dataset.move]);b.setPointerCapture(e.pointerId);};b.onpointerup=b.onpointercancel=()=>keys.delete(moveCodes[b.dataset.move]);});
let last=performance.now();
function frame(now){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.05);last=now;
 if(transition){let t=Math.min((now-transition.start)/1100,1);t=t*t*(3-2*t);camera.position.lerpVectors(transition.from,transition.to,t);controls.target.lerpVectors(transition.fromTarget,transition.toTarget,t);if(t===1)transition=null;}
 if(walking&&!$('#details').open){let forward=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown')),right=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));const scale=3*dt/Math.max(1,Math.hypot(forward,right));camera.position.x+=(-Math.sin(yaw)*forward+Math.cos(yaw)*right)*scale;camera.position.z+=(-Math.cos(yaw)*forward-Math.sin(yaw)*right)*scale;camera.position.x=THREE.MathUtils.clamp(camera.position.x,-8,35);camera.position.z=THREE.MathUtils.clamp(camera.position.z,-11,5);}else if(!walking)controls.update();
 for(const l of labels){l.el.hidden=!showLabels||walking;if(!l.el.hidden){const p=l.pos.clone().project(camera);l.el.hidden=p.z>1||p.z< -1;l.el.style.left=`${(p.x*.5+.5)*viewport.clientWidth}px`;l.el.style.top=`${(-p.y*.5+.5)*viewport.clientHeight}px`;}}
 renderer.render(scene,camera);
}requestAnimationFrame(frame);
