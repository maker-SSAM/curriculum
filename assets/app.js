/* 성취기준 쉽게보기 — 데이터는 assets/data.js(window.CURRICULUM) */
(function () {
  'use strict';
  var D = window.CURRICULUM;
  var AREA_COLORS = { 1: 'var(--a1)', 2: 'var(--a2)', 3: 'var(--a3)', 4: 'var(--a4)' };
  var AREAS = D.bands[0].areas.map(function (a) { return { no: a.no, name: a.name }; });
  var CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮';

  // 성취기준 한 줄씩 펼친 목록
  var ALL = [];
  D.bands.forEach(function (b) {
    b.areas.forEach(function (a) {
      a.subtopics.forEach(function (s) {
        s.standards.forEach(function (st) {
          ALL.push({ code: st.code, text: st.text, exp: st.explanation, band: b.band, area: a.no, areaName: a.name, sub: s.title, subNo: s.no });
        });
      });
    });
  });

  var state = { band: '', area: 0, q: '', expand: false, sel: new Set() };
  var $ = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function norm(s) { return String(s).toLowerCase().replace(/\s+/g, ''); }
  // 띄어쓰기를 무시하고 찾은 곳을 <mark>로
  function hl(text, q) {
    if (!q) return esc(text);
    var nq = norm(q), chars = [], map = [];
    for (var i = 0; i < text.length; i++) { if (!/\s/.test(text[i])) { chars.push(text[i].toLowerCase()); map.push(i); } }
    var hay = chars.join(''), out = '', last = 0, from = 0, k;
    while ((k = hay.indexOf(nq, from)) !== -1) {
      var s = map[k], e = map[k + nq.length - 1] + 1;
      out += esc(text.slice(last, s)) + '<mark>' + esc(text.slice(s, e)) + '</mark>';
      last = e; from = k + nq.length;
    }
    return out + esc(text.slice(last));
  }
  function matches(r, q) {
    if (!q) return true;
    var nq = norm(q);
    return norm(r.code + r.text + r.sub + r.exp.join('')).indexOf(nq) !== -1;
  }
  function visible() {
    return ALL.filter(function (r) {
      return (!state.band || r.band === state.band) && (!state.area || r.area === state.area) && matches(r, state.q);
    });
  }

  function toast(msg) {
    var t = $('toast'); t.textContent = msg; t.classList.add('on');
    clearTimeout(toast._t); toast._t = setTimeout(function () { t.classList.remove('on'); }, 2200);
  }

  /* ---------- 고르기 단추 ---------- */
  function chip(label, pressed, color, onClick) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', pressed ? 'true' : 'false');
    b.innerHTML = (color ? '<span class="sw" style="--c:' + color + '"></span>' : '') + esc(label);
    b.addEventListener('click', onClick);
    return b;
  }
  function renderChips() {
    var bc = $('band-chips'); bc.innerHTML = '';
    [''].concat(D.bands.map(function (b) { return b.band; })).forEach(function (band) {
      bc.appendChild(chip(band || '전체 학년', state.band === band, null, function () { state.band = band; update(); }));
    });
    var ac = $('area-chips'); ac.innerHTML = '';
    ac.appendChild(chip('전체 영역', !state.area, null, function () { state.area = 0; update(); }));
    AREAS.forEach(function (a) {
      ac.appendChild(chip(a.name, state.area === a.no, AREA_COLORS[a.no], function () { state.area = a.no; update(); }));
    });
  }

  /* ---------- 성취기준 목록 ---------- */
  function renderList() {
    var rows = visible(), q = state.q, list = $('list');
    var shown = new Set(rows.map(function (r) { return r.code; }));
    var html = '';
    D.bands.forEach(function (b) {
      var bandRows = rows.filter(function (r) { return r.band === b.band; });
      if (!bandRows.length) return;
      html += '<h2 class="band-h">초등학교 ' + esc(b.band) + '</h2>';
      b.areas.forEach(function (a) {
        var areaRows = bandRows.filter(function (r) { return r.area === a.no; });
        if (!areaRows.length) return;
        var c = AREA_COLORS[a.no], total = 0;
        a.subtopics.forEach(function (s) { total += s.standards.length; });
        html += '<section class="area" style="--c:' + c + '"><h3 class="area-h">(' + a.no + ') ' + esc(a.name) +
          ' <small>' + (areaRows.length === total ? total + '개' : areaRows.length + ' / ' + total + '개') + '</small></h3>';
        a.subtopics.forEach(function (s) {
          var subRows = s.standards.filter(function (st) { return shown.has(st.code); });
          if (!subRows.length) return;
          html += '<h4 class="sub-h" id="sub-' + b.codePrefix + '-' + a.no + '-' + s.no + '">' + CIRCLED[s.no - 1] + ' ' + hl(s.title, q) + '</h4>';
          subRows.forEach(function (st) {
            var on = state.sel.has(st.code);
            html += '<div class="std' + (on ? ' sel' : '') + '"><input type="checkbox" data-code="' + esc(st.code) + '"' + (on ? ' checked' : '') +
              ' aria-label="' + esc(st.code) + ' 고르기"><span class="code">' + hl(st.code, q) + '</span><p class="text">' + hl(st.text, q) + '</p>';
            if (st.explanation.length) {
              html += '<details' + (state.expand || (q && norm(st.explanation.join('')).indexOf(norm(q)) !== -1) ? ' open' : '') +
                '><summary>성취기준 해설</summary><div class="exp">' +
                st.explanation.map(function (x) { return '<p>' + hl(x, q) + '</p>'; }).join('') + '</div></details>';
            }
            html += '</div>';
          });
        });
        html += '<details class="cons"' + (state.expand ? ' open' : '') + '><summary>적용 시 고려 사항 (' + a.considerations.length + ')</summary><ul>' +
          a.considerations.map(function (x) { return '<li>' + hl(x, q) + '</li>'; }).join('') + '</ul></details></section>';
      });
    });
    list.innerHTML = html || '<p class="empty">맞는 성취기준이 없습니다. 낱말을 바꾸거나 학년군·영역을 "전체"로 해 보세요.</p>';
  }

  function targetRows() {
    // 고른 것이 있으면 고른 것, 없으면 지금 보이는 것
    if (state.sel.size) return ALL.filter(function (r) { return state.sel.has(r.code); });
    return visible();
  }
  function renderActions() {
    var v = visible().length, n = state.sel.size;
    $('count').innerHTML = '<b>' + v + '</b>개 보임' + (v !== ALL.length ? ' (전체 ' + ALL.length + '개)' : '') +
      (n ? ' · <b>' + n + '</b>개 고름' : '');
    var what = n ? '고른 ' + n + '개' : '보이는 ' + v + '개';
    $('copy').textContent = what + ' 복사';
    $('csv').textContent = what + ' CSV 저장';
    $('copy').disabled = $('csv').disabled = !(n || v);
    $('sel-none').hidden = !n;
    $('expand').setAttribute('aria-pressed', state.expand ? 'true' : 'false');
    $('expand').textContent = state.expand ? '해설 모두 접기' : '해설 모두 펼치기';
  }

  function update() { renderChips(); renderList(); renderActions(); saveHash(); }

  /* ---------- 내보내기 ---------- */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (ok, fail) {
      var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', '');
      ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy') ? ok() : fail(); } catch (e) { fail(e); }
      document.body.removeChild(ta);
    });
  }
  function csvCell(s) { s = String(s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
  function download(name, text, type) {
    var blob = new Blob([text], { type: type });
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  $('copy').addEventListener('click', function () {
    var rows = targetRows();
    var text = rows.map(function (r) { return r.code + ' ' + r.text; }).join('\n');
    copyText(text).then(function () { toast(rows.length + '개를 복사했습니다'); }, function () { toast('복사하지 못했습니다. 브라우저 권한을 확인해 주세요'); });
  });
  $('csv').addEventListener('click', function () {
    var rows = targetRows();
    var head = ['학년군', '영역', '소주제', '성취기준 코드', '성취기준', '성취기준 해설'];
    var lines = [head.join(',')].concat(rows.map(function (r) {
      return ['초등학교 ' + r.band, r.areaName, r.sub, r.code, r.text, r.exp.join(' ')].map(csvCell).join(',');
    }));
    // 엑셀이 한글을 바르게 읽도록 BOM, 줄바꿈은 CRLF
    download('초등수학_성취기준' + (state.sel.size ? '_고른것' : '') + '.csv', '﻿' + lines.join('\r\n') + '\r\n', 'text/csv;charset=utf-8');
    toast(rows.length + '개를 CSV로 저장했습니다');
  });
  $('md').href = encodeURI(D.files.md);
  $('md').setAttribute('download', '초등수학_성취기준_전문.md');

  $('sel-all').addEventListener('click', function () {
    visible().forEach(function (r) { state.sel.add(r.code); }); renderList(); renderActions();
  });
  $('sel-none').addEventListener('click', function () { state.sel.clear(); renderList(); renderActions(); });
  $('expand').addEventListener('click', function () { state.expand = !state.expand; renderList(); renderActions(); });
  $('list').addEventListener('change', function (e) {
    var cb = e.target; if (!cb.dataset || !cb.dataset.code) return;
    if (cb.checked) state.sel.add(cb.dataset.code); else state.sel.delete(cb.dataset.code);
    cb.closest('.std').classList.toggle('sel', cb.checked); renderActions();
  });
  var qt;
  $('q').addEventListener('input', function (e) {
    clearTimeout(qt); qt = setTimeout(function () { state.q = e.target.value.trim(); renderList(); renderActions(); saveHash(); }, 120);
  });

  /* ---------- 한눈에 보기 ---------- */
  function renderMatrix() {
    var h = '<table><thead><tr><th scope="col">영역</th>' + D.bands.map(function (b) { return '<th scope="col">초등학교 ' + esc(b.band) + '</th>'; }).join('') + '</tr></thead><tbody>';
    AREAS.forEach(function (A) {
      var sum = 0;
      var cells = D.bands.map(function (b) {
        var a = b.areas.filter(function (x) { return x.no === A.no; })[0];
        var n = 0;
        var items = a.subtopics.map(function (s) {
          n += s.standards.length;
          return '<li><button type="button" data-band="' + esc(b.band) + '" data-area="' + a.no + '" data-sub="' + b.codePrefix + '-' + a.no + '-' + s.no + '"><span>' +
            esc(s.title) + '</span><span class="n">' + s.standards.length + '</span></button></li>';
        }).join('');
        sum += n;
        return '<td data-band="초등학교 ' + esc(b.band) + '"><ul>' + items + '</ul><div class="tot">성취기준 ' + n + '개</div></td>';
      });
      h += '<tr style="--c:' + AREA_COLORS[A.no] + '"><th scope="row">(' + A.no + ') ' + esc(A.name) + '<small>' + sum + '개</small></th>' + cells.join('') + '</tr>';
    });
    $('matrix').innerHTML = h + '</tbody></table>';
  }
  $('matrix').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-sub]'); if (!b) return;
    state.band = b.dataset.band; state.area = +b.dataset.area; state.q = ''; $('q').value = '';
    show('standards'); update();
    var el = document.getElementById('sub-' + b.dataset.sub);
    if (el) el.scrollIntoView({ block: 'start' });
  });

  /* ---------- 교육과정 원문 ---------- */
  function renderDoc() {
    var doc = $('doc'), toc = $('toc'), h = '', t = '', id = 0;
    h += '<p class="note">교육부 고시 제2022-33호 [별책 8] 수학과 교육과정 중 <b>공통 교육과정 수학의 초등학교 부분</b>입니다. 내용 체계 표의 중학교 칸과 중학교 성취기준은 넣지 않았습니다. 전체는 공식 <a href="' +
      encodeURI(D.files.pdf) + '">PDF</a>·<a href="' + encodeURI(D.files.hwp) + '">HWP</a>로 볼 수 있습니다.</p>';
    function head(level, text) {
      var a = 'w' + (++id);
      t += '<li class="' + level + '"><a href="#' + a + '">' + esc(text) + '</a></li>';
      return '<' + level + ' id="' + a + '">' + esc(text) + '</' + level + '>';
    }
    D.wonmun.forEach(function (b) {
      if (b.t === 'p') {
        if (b.k === 'h2' || b.k === 'h3' || b.k === 'h4') h += head(b.k, b.text);
        else h += '<p class="' + b.k + '">' + esc(b.text) + '</p>';
      } else if (b.t === 'img') {
        h += '<figure><img src="' + esc(b.src) + '" width="' + b.w + '" height="' + b.h + '" alt="' + esc(b.alt) + '" loading="lazy"></figure>';
      } else if (b.t === 'table') {
        h += renderTable(b);
      } else if (b.t === 'standards') {
        h += renderStandardsOriginal(head);
      }
    });
    doc.innerHTML = h; toc.innerHTML = t;
  }
  function renderTable(tb) {
    var grid = {}, out = '<div class="tbl"><table>';
    tb.cells.forEach(function (c) { grid[c.r + ',' + c.c] = c; });
    for (var r = 0; r < tb.rows; r++) {
      out += '<tr>';
      for (var c = 0; c < tb.cols; c++) {
        var cell = grid[r + ',' + c]; if (!cell) continue;
        var headerish = c === 0 || r <= 3 && !(r === 0 && c > 0);
        var tagn = headerish ? 'th' : 'td';
        out += '<' + tagn + (cell.rs > 1 ? ' rowspan="' + cell.rs + '"' : '') + (cell.cs > 1 ? ' colspan="' + cell.cs + '"' : '') + '>' +
          (tagn === 'th' ? cell.lines.map(esc).join('<br>') : cell.lines.map(function (x) { return '<p>' + esc(x) + '</p>'; }).join('')) + '</' + tagn + '>';
      }
      out += '</tr>';
    }
    return out + '</table></div>';
  }
  function renderStandardsOriginal(head) {
    var h = '';
    D.bands.forEach(function (b) {
      h += head('h4', '[초등학교 ' + b.band + ']');
      b.areas.forEach(function (a) {
        var c = AREA_COLORS[a.no], exps = [];
        h += '<div style="--c:' + c + '"><p class="band-t">(' + a.no + ') ' + esc(a.name) + '</p>';
        a.subtopics.forEach(function (s) {
          h += '<p class="sub-t">' + CIRCLED[s.no - 1] + ' ' + esc(s.title) + '</p>';
          s.standards.forEach(function (st) {
            h += '<p class="src-std"><span class="std-code">' + esc(st.code) + '</span> ' + esc(st.text) + '</p>';
            st.explanation.forEach(function (x, i) { exps.push((i ? '' : '<span class="std-code">' + esc(st.code) + '</span> ') + esc(x)); });
          });
        });
        if (exps.length) h += '<p class="sub-t">(가) 성취기준 해설</p><ul class="bul">' + exps.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>';
        h += '<p class="sub-t">(' + (exps.length ? '나' : '가') + ') 성취기준 적용 시 고려 사항</p><ul class="bul">' +
          a.considerations.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
      });
    });
    return h;
  }

  /* ---------- 보기 바꾸기 · 주소 ---------- */
  var VIEWS = ['standards', 'overview', 'wonmun'];
  function show(v) {
    VIEWS.forEach(function (x) {
      $('view-' + x).hidden = x !== v;
      var tab = $('tab-' + x); tab.setAttribute('aria-selected', x === v ? 'true' : 'false'); tab.tabIndex = x === v ? 0 : -1;
    });
    state.view = v;
    if (document.querySelector('.top')) setTopH();
  }
  document.querySelector('.tabs').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-view]'); if (!b) return;
    show(b.dataset.view); saveHash(); window.scrollTo(0, 0);
  });
  document.querySelector('.tabs').addEventListener('keydown', function (e) {
    var i = VIEWS.indexOf(state.view);
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      i = (i + (e.key === 'ArrowRight' ? 1 : VIEWS.length - 1)) % VIEWS.length;
      show(VIEWS[i]); $('tab-' + VIEWS[i]).focus(); saveHash();
    }
  });
  function saveHash() {
    var p = new URLSearchParams();
    if (state.view && state.view !== 'standards') p.set('v', state.view);
    if (state.band) p.set('b', state.band);
    if (state.area) p.set('a', state.area);
    if (state.q) p.set('q', state.q);
    var s = p.toString();
    try { history.replaceState(null, '', s ? '#' + s : location.pathname + location.search); } catch (e) { /* 파일로 열었을 때 막히면 넘어감 */ }
  }
  function loadHash() {
    var p = new URLSearchParams(location.hash.slice(1));
    var v = p.get('v'); state.band = p.get('b') || ''; state.area = +(p.get('a') || 0); state.q = p.get('q') || '';
    $('q').value = state.q;
    show(VIEWS.indexOf(v) > -1 ? v : 'standards');
  }

  // 붙어 있는 머리 높이(목록 위 단추 줄이 그 아래 붙도록)
  function setTopH() {
    var top = document.querySelector('.top').offsetHeight, act = document.querySelector('.actions');
    var sticky = getComputedStyle(act).position === 'sticky' && !$('view-standards').hidden;
    document.documentElement.style.setProperty('--top-h', top + 'px');
    // 제목·차례로 건너뛸 때 붙어 있는 머리(와 단추 줄)에 가리지 않게
    document.documentElement.style.setProperty('--pad-top', (top + (sticky ? act.offsetHeight : 0) + 12) + 'px');
  }
  window.addEventListener('resize', setTopH);

  $('total').textContent = ALL.length;
  $('f-pdf').href = encodeURI(D.files.pdf); $('f-hwp').href = encodeURI(D.files.hwp); $('f-hwpx').href = encodeURI(D.files.hwpx);
  loadHash(); renderMatrix(); renderDoc(); update(); setTopH();
})();
