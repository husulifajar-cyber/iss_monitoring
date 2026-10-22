(function(){
  // Pengganti fetch("data/*.json") artefak -> google.script.run.getData(); data dikirim gzip+base64.
  var MAP={"data/weekly.json":"weekly","data/today.json":"today","data/daily.json":"daily","data/calleffort.json":"calleffort"};
  var nf=function(st){return {ok:false,status:st,json:function(){return Promise.resolve(null)}}};
  function gunzip(b64){var bin=atob(b64),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
    return new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream("gzip"))).text();}
  var _f=window.fetch;
  window.fetch=function(url){
    var k=MAP[url];
    if(!k){ if(String(url).indexOf("data/")===0) return Promise.resolve(nf(404)); return _f.apply(this,arguments); }
    return new Promise(function(res){
      google.script.run
        .withSuccessHandler(function(b64){
          if(!b64){res(nf(404));return;}
          gunzip(b64).then(function(t){res({ok:true,status:200,json:function(){return Promise.resolve(JSON.parse(t))}})})
                     .catch(function(){res(nf(500))});
        })
        .withFailureHandler(function(){res(nf(500))})
        .getData(k);
    });
  };
  // Kapabilitas artefak: download CSV dibuat lokal di browser; ekspor ke Google Sheets (mcp) belum tersedia.
  window.claude={use:function(n){
    if(n==="downloads") return Promise.resolve({save:function(o){
      var a=document.createElement("a");a.href=URL.createObjectURL(new Blob([o.data],{type:"text/csv;charset=utf-8"}));
      a.download=o.filename;document.body.appendChild(a);a.click();
      setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1500);return Promise.resolve();}});
    return Promise.resolve(null);
  }};
})();
