import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the section to replace
old_start = 'const TRANSLIT_MODES = ['
start_idx = content.find(old_start)

# Find where renderTranslit ends (line before setTranslitMode)
render_end = 'container.innerHTML = html;\n}\n\nfunction setTranslitMode('
render_end_idx = content.find(render_end, start_idx)
if render_end_idx > 0:
    render_end_idx += len('container.innerHTML = html;\n}\n')

# Find where doTranslit ends (before copyTranslit)
copy_start = 'function copyTranslit()'
copy_idx = content.find(copy_start, start_idx)

# Find setTranslitMode
settrans_start = 'function setTranslitMode('
settrans_idx = content.find(settrans_start, start_idx)

# Find doTranslit
dotrans_start = 'function doTranslit('
dotrans_idx = content.find(dotrans_start, start_idx)

# Find the end of doTranslit function  
# Look for the closing brace + blank line before copyTranslit
# doTranslit ends right before the blank line before copyTranslit
do_end = content.rfind('\n\n', dotrans_idx, copy_idx)
# The doTranslit function body ends just before the double newline
# Let me be more precise - find the matching brace
brace_count = 0
func_end = dotrans_idx
in_func = False
for i in range(dotrans_idx, len(content)):
    c = content[i]
    if c == '{':
        brace_count += 1
        in_func = True
    elif c == '}':
        brace_count -= 1
        if in_func and brace_count == 0:
            func_end = i + 1
            break

print(f"start_idx: {start_idx}")
print(f"settrans_idx: {settrans_idx}")
print(f"dotrans_idx: {dotrans_idx}")
print(f"func_end: {func_end}")

new_code = """let currentTranslitPage = 'zh-cyr';
let translitDir = 'zh2kk';

// Keep cyr2Latin for internal use (Latin alphabet display)
function cyr2Latin(text){
  const m={'а':'a','ә':'ä','б':'b','в':'v','г':'g','ғ':'ğ','д':'d','е':'e',
    'ё':'ë','ж':'j','з':'z','и':'i','й':'ı','к':'k','қ':'q','л':'l','м':'m',
    'н':'n','ң':'ñ','о':'o','ө':'ö','п':'p','р':'r','с':'s','т':'t','у':'y',
    'ұ':'ū','ү':'ü','ф':'f','х':'h','һ':'h','ц':'ts','ч':'ch','ш':'ş','щ':'şş',
    'ъ':'','ы':'y','і':'i','ь':'','э':'è','ю':'iu','я':'ia',
    'А':'A','Ә':'Ä','Б':'B','В':'V','Г':'G','Ғ':'Ğ','Д':'D','Е':'E',
    'Ё':'Ë','Ж':'J','З':'Z','И':'I','Й':'Y','К':'K','Қ':'Q','Л':'L','М':'M',
    'Н':'N','Ң':'Ñ','О':'O','Ө':'Ö','П':'P','Р':'R','С':'S','Т':'T','У':'Y',
    'Ұ':'Ū','Ү':'Ü','Ф':'F','Х':'X','Һ':'H','Ц':'Ts','Ч':'Ch','Ш':'Ş','Щ':'Şş',
    'Ъ':'','Ы':'Y','І':'I','Ь':'','Э':'E','Ю':'Iu','Я':'Ia'};
  let r='';
  for(let c of text){
    if(m[c]) r+=m[c];
    else r+=c;
  }
  return r;
}

function renderTranslit(prefix){
  const container = document.getElementById(prefix+'-translit');
  if(!container) return;
  currentTranslitPage = prefix;
  translitDir = 'zh2kk';

  let html = '<div class="section-title">🔄 翻译工具（百度翻译）</div>'
    + '<div style="font-size:.82em;color:var(--text2);margin-bottom:10px">输入中文或哈萨克文，自动翻译</div>'
    + '<div class="translit-area">'
    + '<div class="translit-tabs" style="margin-bottom:8px">'
    + '<button class="active" id="translitDirBtn" onclick="swapTranslitDir()">中文 → Қазақша</button>'
    + '</div>'
    + '<div class="translit-row"><textarea id="translitInput" placeholder="输入中文或哈萨克文..."></textarea></div>'
    + '<div class="translit-actions">'
    + '<button class="primary" onclick="doTranslit()">🌐 翻译</button>'
    + '<button onclick="swapTranslitDir()">🔄 互换语言</button>'
    + '<button onclick="copyTranslit()">📋 复制结果</button>'
    + '<button class="danger" onclick="clearTranslit()">🗑️ 清空</button>'
    + '<button onclick="toggleHistory()">📜 历史</button>'
    + '</div>'
    + '<div class="translit-row"><textarea id="translitOutput" placeholder="翻译结果..." readonly style="min-height:80px"></textarea></div>'
    + '<div id="translitError" class="error-msg" style="display:none"></div>'
    + '<div id="translitHistory" class="history-list" style="display:none"></div>'
    + '<div class="batch-zone" onclick="document.getElementById(\\'batchFile\\').click()" ondragover="this.classList.add(\\'dragover\\')" ondragleave="this.classList.remove(\\'dragover\\')" ondrop="handleBatchDrop(event,\\'' + prefix + '\\')">'
    + '📄 上传 TXT 文件 → 自动翻译并下载'
    + '<span style="display:block;font-size:.78em;color:var(--text3);margin-top:4px">一行一句自动翻译，完成后自动下载</span>'
    + '<input type="file" id="batchFile" accept=".txt" onchange="handleBatchFile(event,\\'' + prefix + '\\')" style="display:none">'
    + '</div></div>';
  container.innerHTML = html;
}

function swapTranslitDir(){
  translitDir = translitDir==='zh2kk' ? 'kk2zh' : 'zh2kk';
  const btn = document.getElementById('translitDirBtn');
  btn.textContent = translitDir==='zh2kk' ? '中文 → Қазақша' : 'Қазақша → 中文';
}

function doTranslit(){
  const input = document.getElementById('translitInput');
  const output = document.getElementById('translitOutput');
  const error = document.getElementById('translitError');
  if(!input||!output) return;
  const text = input.value.trim();
  if(!text){ output.value=''; return; }

  output.value = '翻译中...';
  const to = translitDir==='zh2kk' ? 'kaz' : 'zh';
  const from = translitDir==='zh2kk' ? 'zh' : 'kaz';

  baiduTranslate(text, from, to).then(result=>{
    if(result){
      output.value = result;
      state.history.unshift({src:text,dst:result,time:new Date().toLocaleString()});
      if(state.history.length>50) state.history.pop();
      saveState();
      error.style.display='none';
    } else {
      output.value = '';
      error.textContent = '翻译失败，请检查网络或稍后再试';
      error.style.display='block';
    }
  });
}"""

new_content = content[:start_idx] + new_code + content[func_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done! File updated.")
