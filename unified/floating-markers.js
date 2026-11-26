/* Map-independent Canvas 2D team medallions. All coordinates use board pixels. */
'use strict';
window.QuestMarkers=(()=>{
 function ellipse(c,x,y,rx,ry,fill,stroke,w=1){c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);if(fill){c.fillStyle=fill;c.fill()}if(stroke){c.lineWidth=w;c.strokeStyle=stroke;c.stroke()}}
 function slot(i){return [[-18,-5],[18,-5],[-36,-40],[0,-40],[36,-40],[0,-75]][i]||[0,0]}
 function pose(q,t){const moving=q.v.duration>0,phase=Number(q.team.symbol)||1;const idle=2.2*Math.sin(t*.003+phase*1.17);const hop=moving?6*Math.abs(Math.sin((q.v.d-q.v.start)/13)):0;const age=t-(q.v.t0+q.v.lastDuration);const land=!moving&&age>=0&&age<350?Math.sin(age/350*Math.PI)*3:0;return {x:q.x,y:q.y-31-idle-hop+land,r:q.tied?14.5:17,hover:idle+hop-land}}
 function badge(c,p,team,active,t){let {x,y,r}=p;c.save();c.translate(x,y);if(active){ellipse(c,0,0,r+4+1.5*Math.sin(t*.005),r+4+1.5*Math.sin(t*.005),null,'#fff3bb',2.4)}
 // Bevelled medallion with depth, reflected highlight and high-contrast symbol.
 ellipse(c,0,3,r+1,r+1,'#112b36','#f7edca',1.6);let g=c.createRadialGradient(-r*.35,-r*.5,1,0,0,r*1.13);g.addColorStop(0,'#ffffff');g.addColorStop(.25,team.color);g.addColorStop(.78,team.color);g.addColorStop(1,'#142838');ellipse(c,0,0,r,r,g,'#fff3d9',1.7);ellipse(c,0,0,r-3,r-3,null,'#ffffff48',1);ellipse(c,-r*.33,-r*.57,r*.29,r*.11,'#ffffff99');c.font=`800 ${Math.round(r*1.25)}px system-ui`;c.textAlign='center';c.textBaseline='middle';c.lineWidth=3.2;c.strokeStyle='#15262f';c.fillStyle='#fff9eb';c.strokeText(team.symbol,0,1);c.fillText(team.symbol,0,1);c.restore()}
 function tether(c,anchor,p){c.save();c.strokeStyle='#152c35cc';c.lineWidth=3;c.beginPath();c.moveTo(anchor.x,anchor.y-8);c.lineTo(p.x,p.y+p.r*.68);c.stroke();c.strokeStyle='#fff1c8d9';c.lineWidth=1.2;c.stroke();c.restore()}
 return {slot,pose,badge,tether};
})();
