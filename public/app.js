const state = {
  user: JSON.parse(localStorage.getItem('script_user') || 'null'),
  scripts: [],
  room: null,
  socket: null,
  localAnswers: {},
  musicOn: localStorage.getItem('script_music_on') === '1',
  currentAudio: null, // 当前播放的音频
};

const $ = (selector) => document.querySelector(selector);
const ERROR_TEXT = {
  need_3_players: '需要 3 名玩家到齐后才能开始。',
  all_players_must_choose_character: '所有玩家都需要先选择角色。',
  character_must_be_unique: '角色不能重复选择。',
  only_host_can_start: '只有房主可以开始游戏。',
  room_full: '房间人数已满。',
  room_not_waiting: '该房间已经开始或结束，不能加入。',
  character_taken: '该角色已经被其他玩家选择。',
  only_host_can_advance: '只有房主可以推进轮次。',
  only_host_can_delete: '只有房主可以删除房间。',
  room_not_answering: '当前还没有进入最终作答阶段。',
  must_finish_all_rounds: '需要完成全部搜证轮次后才能进入最终作答。',
  script_not_found: '没有找到这个剧本。',
  only_host_can_release_clue: '只有房主可以释放公开线索。',
  can_only_release_current_round_clue: '只能释放当前轮次的线索。',
  clue_not_found: '没有找到这张线索牌。',
};

function api(path, options = {}) {
  return fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  }).then(async (res) => {
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(ERROR_TEXT[data.error] || data.error || '请求失败');
    return data;
  });
}

function toast(message) {
  const host = $('#toastHost');
  if (!host) return;
  const item = document.createElement('div');
  item.className = 'toast';
  item.textContent = message;
  host.appendChild(item);
  setTimeout(() => item.classList.add('show'), 20);
  setTimeout(() => {
    item.classList.remove('show');
    setTimeout(() => item.remove(), 220);
  }, 2600);
}

function askConfirm(message, title = '请确认') {
  const dialog = $('#confirmDialog');
  $('#confirmTitle').textContent = title;
  $('#confirmMessage').textContent = message;
  dialog.showModal();
  return new Promise((resolve) => {
    const cleanup = (value) => {
      $('#okConfirm').onclick = null;
      $('#cancelConfirm').onclick = null;
      dialog.oncancel = null;
      dialog.close();
      resolve(value);
    };
    $('#okConfirm').onclick = () => cleanup(true);
    $('#cancelConfirm').onclick = () => cleanup(false);
    dialog.oncancel = () => cleanup(false);
  });
}

function applyRoomResponse(data, fallbackMessage = '') {
  state.room = data;
  if (data.deleted_rooms?.length) toast(`已自动清理 ${data.deleted_rooms.length} 个仅自己在等待的旧房间。`);
  if (fallbackMessage) toast(fallbackMessage);
}

function showView(name) {
  if (name === 'room' && !state.room?.room) {
    toast('你还没有进入房间，请先创建或加入房间。');
    name = 'hall';
  }
  $('#login').classList.toggle('hidden', !!state.user);
  document.querySelectorAll('.view').forEach((view) => view.classList.add('hidden'));
  if (state.user) $(`#${name}`).classList.remove('hidden');
  document.querySelectorAll('.nav-btn').forEach((btn) => btn.classList.toggle('active', btn.dataset.view === name));
  
  // 离开房间时暂停音乐
  if (name !== 'room') {
    const audio = $('#bgMusic');
    if (audio) audio.pause();
  }
}

function currentPlayer() {
  return state.room?.players.find((player) => player.open_id === state.user.open_id);
}

function myCharacter() {
  const player = currentPlayer();
  return state.room?.script.characters.find((character) => character.id === player?.character_id);
}

function isHost() {
  return state.room?.room.host_open_id === state.user.open_id;
}

function requiredPlayers() {
  return Number(state.room?.script.player || 0);
}

function roundCount() {
  return Number(state.room?.script.roundCount || state.room?.script.rounds?.length || 0);
}

function assetUrl(path, fallback = '') {
  return path || fallback;
}

function hasSubmitted(openId = state.user.open_id) {
  return state.room?.answers?.some((answer) => answer.open_id === openId);
}

function syncMusicSource() {
  const audio = $('#bgMusic');
  const music = state.room?.script?.music || state.scripts.find((script) => script.music)?.music || '/sleep.mp3';
  if (audio && music && audio.getAttribute('src') !== music) audio.src = music;
}

async function setMusic(on) {
  state.musicOn = on;
  localStorage.setItem('script_music_on', on ? '1' : '0');
  const button = $('#musicToggle');
  const audio = $('#bgMusic');
  syncMusicSource();
  if (button) button.textContent = on ? '♪ 音乐开' : '♪ 音乐关';
  if (!audio) return;
  if (!on) {
    audio.pause();
    return;
  }
  try {
    await audio.play();
  } catch {
    state.musicOn = false;
    localStorage.setItem('script_music_on', '0');
    if (button) button.textContent = '♪ 音乐关';
    toast('浏览器需要点击后才能播放音乐，请再点一次音乐按钮。');
  }
}

async function login() {
  const openId = $('#openIdInput').value.trim() || `demo_${Math.random().toString(16).slice(2, 8)}`;
  const nickname = $('#nicknameInput').value.trim() || `玩家${openId.slice(-4)}`;
  try {
    state.user = await api('/api/login', {
      method: 'POST',
      body: JSON.stringify({ open_id: openId, nickname }),
    });
    localStorage.setItem('script_user', JSON.stringify(state.user));
    await loadHall();
    showView('hall');
  } catch (err) {
    toast(err.message);
  }
}

async function loadHall() {
  const scriptData = await api('/api/scripts');
  state.scripts = scriptData.scripts;
  renderScripts();
  await renderRooms();
}

function renderScripts() {
  $('#scriptGrid').innerHTML = state.scripts.map((script) => `
    <article class="script-card">
      <div class="cover" style="--cover-image: url('${assetUrl(script.cover, '/临时集团.png')}')">
        <b>${script.scene}</b>
        <span>${script.scriptName}</span>
      </div>
      <div class="card-body">
        <h2>${script.scriptName}</h2>
        <p>${script.introduce}</p>
        <div class="meta"><span>👥 ${script.player}人</span><span>⏱ ${script.duration}</span><span>⭐ 轻松本</span></div>
        <div class="card-actions one">
          <button class="secondary" onclick="createRoom(${script.scriptId})">创建 / 回到我的房间</button>
        </div>
      </div>
    </article>
  `).join('');
}

async function renderRooms() {
  const data = await api(`/api/rooms?open_id=${encodeURIComponent(state.user.open_id)}`);
  $('#roomList').innerHTML = data.rooms.length ? data.rooms.map((room) => `
    <div class="room-item">
      <div>
        <h3>${room.title} · ${room.room_id}</h3>
        <p>${statusText(room.status)}，${room.player_count} 人${room.host_open_id === state.user.open_id ? ' · 我创建的' : ''}</p>
      </div>
      <button class="primary" onclick="joinRoom('${room.room_id}')">进入房间</button>
    </div>
  `).join('') : '<div class="panel"><div class="empty-icon">♙</div><h2>暂无房间</h2><p>创建一个新房间开始游戏吧。</p></div>';
}

function statusText(status) {
  return ({ waiting: '等待中', playing: '游戏中', answering: '最终作答中', finished: '已结算' })[status] || status;
}

async function createRoom(scriptId) {
  try {
    applyRoomResponse(await api('/api/rooms', {
      method: 'POST',
      body: JSON.stringify({ ...state.user, script_id: scriptId }),
    }));
    enterRoom();
  } catch (err) {
    toast(err.message);
  }
}

async function joinRoom(roomId) {
  try {
    applyRoomResponse(await api(`/api/rooms/${roomId}/join`, {
      method: 'POST',
      body: JSON.stringify(state.user),
    }));
    enterRoom();
  } catch (err) {
    toast(err.message);
  }
}

async function joinRoomByInput() {
  const roomId = $('#roomIdInput').value.trim().toUpperCase();
  if (!roomId) return toast('请先输入房间号。');
  await joinRoom(roomId);
}

function enterRoom() {
  state.localAnswers = {};
  showView('room');
  connectWs();
  renderRoom();
  // 进入房间时根据设置播放音乐
  if (state.musicOn) {
    syncMusicSource();
    const audio = $('#bgMusic');
    if (audio) {
      audio.play().catch(() => {
        toast('浏览器需要点击后才能播放音乐，请再点一次音乐按钮。');
      });
    }
  }
}

function connectWs() {
  if (state.socket) state.socket.close();
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  state.socket = new WebSocket(`${protocol}://${location.host}/ws?room_id=${state.room.room.room_id}&open_id=${state.user.open_id}`);
  state.socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'room_state') {
      state.room = message.data;
      renderRoom();
    } else if (message.type === 'room_deleted') {
      state.room = null;
      toast('房间已被删除。');
      loadHall().then(() => showView('hall'));
    }
  };
}

function renderRoom() {
  if (!state.room?.room) return;
  const { room, script, players } = state.room;
  syncMusicSource();
  $('#roomTitle').textContent = `${script.scriptName} · ${room.room_id}`;
  $('#roomSub').textContent = room.status === 'playing' ? `游戏中 · 第 ${room.current_round} 轮` : statusText(room.status);
  $('#startBtn').classList.toggle('hidden', !isHost() || room.status !== 'waiting');
  $('#deleteRoomBtn').classList.toggle('hidden', !isHost());
  $('#waitingStage').classList.toggle('hidden', room.status !== 'waiting');
  $('#playingStage').classList.toggle('hidden', room.status === 'waiting');
  renderFlowSteps();
  renderPlayers(players, script);
  renderCharacters(script);
  renderHint();
  if (room.status !== 'waiting') renderRound();
}

function renderFlowSteps() {
  const status = state.room.room.status;
  const finalReady = status === 'finished';
  const steps = [
    ['waiting', '1 等待 / 选角'],
    ['playing', '2 搜证问答'],
    ['answering', '3 个人作答'],
    ['finished', '4 结算复盘'],
  ];
  $('#flowSteps').innerHTML = steps.map(([key, label]) => {
    const active = (key === 'waiting' && status === 'waiting') || (key === 'playing' && status === 'playing') || (key === 'answering' && status === 'answering') || (key === 'finished' && finalReady);
    const done = (key === 'waiting' && status !== 'waiting') || (key === 'playing' && ['answering', 'finished'].includes(status)) || (key === 'answering' && finalReady);
    return `<span class="flow-step ${active ? 'active' : ''} ${done ? 'done' : ''}">${label}</span>`;
  }).join('');
}

function renderHint() {
  const { players, room, script } = state.room;
  const chosen = players.filter((p) => p.character_id).length;
  if (room.status === 'waiting') {
    $('#roomHint').textContent = `开始条件：${players.length}/${script.player} 人，${chosen}/${script.player} 人已选角。`;
  } else if (room.status === 'playing') {
    const round = script.rounds?.[0];
    const released = round?.publicClues?.filter((clue) => clue.released).length || 0;
    const total = round?.publicClues?.length || 0;
    $('#roomHint').textContent = `房主按轮次推进搜证，当前轮线索 ${released}/${total} 已公开。`;
  } else if (room.status === 'answering') {
    $('#roomHint').textContent = `最终作答中：${state.room.answers.length}/${players.length} 人已提交，全部提交后显示胜利者和标准答案。`;
  } else {
    $('#roomHint').textContent = `本局已结束，房主可删除房间后重新创建。`;
  }
}

function renderPlayers(players, script) {
  $('#players').innerHTML = players.map((player, index) => {
    const character = script.characters.find((item) => item.id === player.character_id);
    const isMe = player.open_id === state.user.open_id;
    const submitted = hasSubmitted(player.open_id);
    return `<div class="player ${isMe ? 'me' : ''}">
      #${index + 1} ${player.nickname}${state.room.room.host_open_id === player.open_id ? ' <b>房主</b>' : ''}
      <small>${character ? `${character.name} · ${character.roleTag}` : '未选择角色'} ${player.ready ? '✅' : ''} ${submitted ? '已提交答案' : ''}</small>
    </div>`;
  }).join('');
}

function renderCharacters(script) {
  const selectedIds = state.room.players.map((player) => player.character_id).filter(Boolean);
  $('#characterCards').innerHTML = script.characters.map((character) => {
    const selected = selectedIds.includes(character.id);
    const mine = currentPlayer()?.character_id === character.id;
    return `<div class="character ${mine ? 'selected' : ''}">
      <h3>${character.name}</h3>
      <p>${character.introduce}</p>
      <small>${character.roleTag} · ${character.publicGoal}</small>
      <button class="pick" ${selected && !mine ? 'disabled' : ''} onclick="chooseCharacter(${character.id})">${mine ? '查看我的角色' : selected ? '已被选择' : '选择角色'}</button>
    </div>`;
  }).join('');
}

async function chooseCharacter(characterId) {
  const mine = currentPlayer()?.character_id === characterId;
  if (mine) {
    openRoleDialog();
    return;
  }
  try {
    state.room = await api(`/api/rooms/${state.room.room.room_id}/choose`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id, character_id: characterId }),
    });
    renderRoom();
    openRoleDialog();
  } catch (err) {
    toast(err.message);
  }
}

function openRoleDialog() {
  const character = myCharacter();
  if (!character) return;
  const privateData = character.data;
  $('#roleContent').innerHTML = `
    <p class="eyebrow">你的角色信息</p>
    <h2>${character.name}</h2>
    <div class="scene"><b>${character.roleTag}</b><p>${character.introduce}</p></div>
    ${privateData ? `
      <div class="scene secret"><b>你的秘密</b><p>${privateData.secret}</p></div>
      <div class="scene discovery"><b>你的线索</b>${(privateData.discovery || []).map((item) => `<p><b>${item.keyword}</b>：${item.content}</p>`).join('')}</div>
      <div class="scene"><b>角色任务</b><p>${(privateData.task || '').replaceAll('\n', '<br>')}</p></div>
    ` : '<div class="scene"><b>提示</b><p>只有已选择的本人角色会显示私密剧本。</p></div>'}
  `;
  $('#roleDialog').showModal();
}

async function startGame() {
  try {
    state.room = await api(`/api/rooms/${state.room.room.room_id}/start`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id }),
    });
    renderRoom();
  } catch (err) {
    toast(err.message);
  }
}

async function changeRound(next) {
  if (!isHost()) return toast('只有房主可以推进轮次。');
  const round = Math.max(1, Math.min(roundCount(), state.room.room.current_round + next));
  try {
    state.room = await api(`/api/rooms/${state.room.room.room_id}/round`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id, round }),
    });
    renderRoom();
  } catch (err) {
    toast(err.message);
  }
}

async function enterAnswering() {
  if (!isHost()) return toast('只有房主可以推进流程。');
  try {
    state.room = await api(`/api/rooms/${state.room.room.room_id}/answering`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id }),
    });
    renderRoom();
  } catch (err) {
    toast(err.message);
  }
}

function renderRound() {
  if (state.room.room.status === 'finished') {
    $('#prevRound').disabled = true;
    $('#nextRound').disabled = true;
    $('#nextRound').textContent = '已结算';
    renderResult();
    return;
  }
  if (state.room.room.status === 'answering') {
    $('#roundBadge').textContent = '最终作答';
    $('#prevRound').disabled = true;
    $('#nextRound').disabled = true;
    $('#nextRound').textContent = '等待提交';
    $('#roundContent').innerHTML = renderFinalQuestions();
    return;
  }
  const round = state.room.script.rounds.find((item) => item.round === state.room.room.current_round);
  if (!round) {
    $('#roundContent').innerHTML = '<div class="scene"><h2>等待轮次数据</h2><p>当前轮次内容尚未下发，请稍后刷新。</p></div>';
    return;
  }
  $('#roundBadge').textContent = `第 ${round.round} 轮 · ${round.title} · ${round.duration}`;
  $('#prevRound').disabled = !isHost() || round.round === 1;
  $('#nextRound').disabled = !isHost();
  $('#nextRound').textContent = round.round === roundCount() ? '进入最终作答' : '下一轮';
  $('#nextRound').onclick = round.round === roundCount() ? enterAnswering : () => changeRound(1);
  $('#roundContent').innerHTML = `
    <div class="scene">
      <h2>${round.title}</h2>
      <p>${round.scenePrompt}${audioButton(round.scenePrompt_audio, '播放场景')}</p>
      ${round.hostGuide ? `<p><b>主持提示：</b>${round.hostGuide}${audioButton(round.hostGuide_audio, '播放提示')}</p>` : ''}
    </div>
    ${renderClueProgress(round)}
    ${renderMyRoleMini()}
    <div class="clue-grid">${round.publicClues.map((clue) => renderClueCard(round.round, clue)).join('')}</div>
    ${round.questions.map((question) => {
      const text = typeof question === 'string' ? question : question.text;
      const audio = typeof question === 'object' ? question.audio : null;
      return `<div class="question">讨论问题：${text}${audioButton(audio, '播放问题')}</div>`;
    }).join('')}
  `;
}

function renderClueProgress(round) {
  const total = round.publicClues.length;
  const released = round.publicClues.filter((clue) => clue.released).length;
  const percent = total ? Math.round((released / total) * 100) : 0;
  return `<div class="clue-progress">
    <div><b>搜证公开进度</b><span>${released}/${total} 张已公开</span></div>
    <meter min="0" max="${total || 1}" value="${released}"></meter>
    <small>${percent}% · ${isHost() ? '主持可点击线索卡逐张释放' : '等待主持释放更多线索'}</small>
  </div>`;
}

function renderClueCard(round, clue) {
  if (clue.released) {
    return `<div class="clue revealed">
      <b>${clue.keyword}</b>
      <p>${clue.content}${audioButton(clue.content_audio, '播放线索')}</p>
    </div>`;
  }
  return `<div class="clue locked">
    <span class="clue-mark">?</span>
    <b>${clue.keyword}</b>
    <p>线索尚未公开，等待玩家搜证或主持翻牌。</p>
    ${isHost() ? `<button class="primary" onclick="releaseClue(${round}, ${clue.index})">释放这张线索</button>` : '<small>等待主持释放</small>'}
  </div>`;
}

async function releaseClue(round, clueIndex) {
  if (!isHost()) return toast('只有房主可以释放公开线索。');
  try {
    state.room = await api(`/api/rooms/${state.room.room.room_id}/release-clue`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id, round, clue_index: clueIndex }),
    });
    renderRoom();
    toast('线索已公开，所有玩家将同步看到。');
  } catch (err) {
    toast(err.message);
  }
}

function renderMyRoleMini() {
  const character = myCharacter();
  if (!character) return '';
  return `<div class="my-role-card">
    <b>我的发言身份：${character.name}</b>
    <p>${character.roleTag}。你可以结合私密线索发言，但不要直接把所有秘密一次性摊开。</p>
    <button class="ghost" onclick="openRoleDialog()">查看我的角色卡</button>
  </div>`;
}

function renderFinalQuestions() {
  const disabled = hasSubmitted() ? 'disabled' : '';
  return `<h2>最终还原 / 个人作答</h2>
    <p>这里不再提前展示标准答案。每名玩家独立选择，全部提交后系统按答对数量判定胜利者。</p>
    <div class="submit-progress">已提交：${state.room.answers.length}/${state.room.players.length}</div>
    ${state.room.script.finalQuestions.map((item) => `
      <div class="answer-card">
        <b>${item.title}</b>
        ${item.options.map((option) => {
          // 从 state.localAnswers 恢复选中状态，防止 WebSocket 重新渲染时丢失选择
          const checked = state.localAnswers[String(item.id)] === option ? 'checked' : '';
          return `
            <label class="option"><input type="radio" name="q_${item.id}" value="${option}" ${disabled} ${checked} onchange="state.localAnswers['${item.id}']=this.value"> ${option}</label>
          `;
        }).join('')}
      </div>
    `).join('')}
    <button class="primary" ${disabled} onclick="submitAnswers()">${hasSubmitted() ? '已提交，等待其他玩家' : '提交我的答案'}</button>`;
}

async function submitAnswers() {
  const missing = state.room.script.finalQuestions.filter((item) => !state.localAnswers[String(item.id)]);
  if (missing.length) return toast('请先完成所有最终选择。');
  try {
    state.room = await api(`/api/rooms/${state.room.room.room_id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id, answers: state.localAnswers }),
    });
    renderRoom();
  } catch (err) {
    toast(err.message);
  }
}

function renderResult() {
  const { script, answers, players } = state.room;
  const rewards = script.answers?.rewards || {};
  
  $('#roundBadge').textContent = '结算复盘';
  $('#roundContent').innerHTML = `
    <h2>📊 答题情况</h2>
    <div class="player-results">
      ${answers.map((answer, index) => {
        const player = players.find((p) => p.open_id === answer.open_id);
        const character = script.characters.find((c) => c.id === player?.character_id);
        const isWinner = answer.is_winner;
        const rewardMessage = isWinner ? rewards.winner_message : rewards.loser_message;
        
        return `<div class="result-card ${isWinner ? 'winner' : ''}">
          <div class="result-header">
            <span class="result-rank">#${index + 1}</span>
            <span class="result-name">${player?.nickname || answer.open_id}</span>
            ${character ? `<span class="result-character">${character.name}</span>` : ''}
          </div>
          <div class="result-score">
            <span class="score-big">${answer.score}/${script.finalQuestions.length}</span>
            <span class="score-label">题正确</span>
            ${isWinner ? '<span class="trophy">🏆</span>' : ''}
          </div>
          ${rewardMessage ? `<div class="result-reward ${isWinner ? 'winner-reward' : 'loser-reward'}">${rewardMessage}</div>` : ''}
        </div>`;
      }).join('')}
    </div>
    
    <div class="scene"><b>标准答案</b><p>${script.answers?.truth || '已结算后由后端下发。'}</p></div>
    ${renderAnswerReview()}
    <div class="scene"><b>关键证据</b><p>${(script.answers?.keyEvidence || []).join('、')}</p></div>
    <div class="scene"><b>主持复盘</b><p>${script.answers?.hostReveal || ''}</p></div>
  `;
}

function renderAnswerReview() {
  const { script, answers, players } = state.room;
  if (!script.finalQuestions?.length || !answers.length) return '';
  return `<div class="answer-review scene">
    <b>个人答案 vs 标准答案</b>
    <div class="review-table">
      ${script.finalQuestions.map((question) => `
        <div class="review-row header"><span>${question.title}</span><span>标准答案：${question.answer}</span></div>
        ${answers.map((answer) => {
          const player = players.find((p) => p.open_id === answer.open_id);
          const selected = answer.answers?.[String(question.id)] || '未作答';
          const correct = selected === question.answer;
          return `<div class="review-row ${correct ? 'right' : 'wrong'}"><span>${player?.nickname || answer.open_id}</span><span>${selected} ${correct ? '✅' : '❌'}</span></div>`;
        }).join('')}
      `).join('')}
    </div>
  </div>`;
}

async function copyInviteText() {
  if (!state.room?.room) return toast('当前没有可复制的房间。');
  const roomId = state.room.room.room_id;
  const scriptName = state.room.script.scriptName;
  const url = `${window.location.origin}${window.location.pathname}?room=${roomId}`;
  const text = `🎭 剧本杀邀请\n剧本：《${scriptName}》\n房间号：${roomId}\n\n点击链接加入：\n${url}`;
  
  try {
    // 方法1：尝试现代剪贴板 API（需要 HTTPS）
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      toast('邀请链接已复制，发给好友即可！');
      return;
    }
  } catch (err) {
    console.log('剪贴板 API 失败，尝试降级方案', err);
  }
  
  // 方法2：降级到 document.execCommand（兼容 HTTP）
  try {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textarea);
    
    if (success) {
      toast('邀请链接已复制，发给好友即可！');
    } else {
      throw new Error('复制失败');
    }
  } catch (err) {
    // 方法3：最终降级，显示文本让用户手动复制
    toast('请手动复制下方文本：');
    setTimeout(() => toast(text), 500);
  }
}

async function deleteRoom() {
  const message = state.room?.room.status === 'playing' || state.room?.room.status === 'answering'
    ? '房间正在进行中，确定强制删除吗？删除后所有玩家都会退出。'
    : '确定删除自己创建的房间吗？删除后可重新创建。';
  if (!await askConfirm(message, '删除房间')) return;
  try {
    await api(`/api/rooms/${state.room.room.room_id}/delete`, {
      method: 'POST',
      body: JSON.stringify({ open_id: state.user.open_id }),
    });
    state.room = null;
    if (state.socket) state.socket.close();
    await loadHall();
    showView('hall');
  } catch (err) {
    toast(err.message);
  }
}

function bindEvents() {
  $('#loginBtn').onclick = login;
  $('#backHall').onclick = () => showView('hall');
  $('#startBtn').onclick = startGame;
  $('#deleteRoomBtn').onclick = deleteRoom;
  $('#prevRound').onclick = () => changeRound(-1);
  $('#nextRound').onclick = () => changeRound(1);
  $('#joinByIdBtn').onclick = joinRoomByInput;
  $('#closeRole').onclick = () => $('#roleDialog').close();
  $('#copyRoomBtn').onclick = copyInviteText;
  $('#musicToggle').onclick = () => setMusic(!state.musicOn);
  document.querySelectorAll('.nav-btn[data-view]').forEach((btn) => btn.onclick = () => state.user && showView(btn.dataset.view));
  document.querySelectorAll('.tab').forEach((tab) => tab.onclick = () => {
    document.querySelectorAll('.tab').forEach((item) => item.classList.toggle('active', item === tab));
    $('#scriptGrid').classList.toggle('hidden', tab.dataset.tab !== 'scripts');
    $('#roomList').classList.toggle('hidden', tab.dataset.tab !== 'rooms');
    if (tab.dataset.tab === 'rooms') renderRooms();
  });
  
  // 粘贴智能提取房间号
  $('#roomIdInput').addEventListener('paste', (e) => {
    setTimeout(() => {
      const text = e.target.value;
      const match = text.match(/[A-Z0-9]{6}/);
      if (match && match[0] !== text) {
        $('#roomIdInput').value = match[0];
        toast(`已提取房间号：${match[0]}`);
      }
    }, 10);
  });
}

// URL参数自动填充房间号
function initRoomFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  const roomId = urlParams.get('room');
  
  if (roomId) {
    $('#roomIdInput').value = roomId.toUpperCase();
    if (state.user) {
      toast(`检测到房间号 ${roomId}，请点击"加入房间"`);
    } else {
      toast(`检测到房间号 ${roomId}，请先登录`);
    }
  }
}

// ==================== TTS 音频播放功能 ====================

function playAudio(audioPath) {
  if (!audioPath) return;
  
  // 停止当前播放的音频
  if (state.currentAudio) {
    state.currentAudio.pause();
    state.currentAudio = null;
  }
  
  // 创建新的音频对象
  const audio = new Audio(audioPath);
  state.currentAudio = audio;
  
  audio.play().catch((err) => {
    console.error('音频播放失败:', err);
    toast('音频播放失败，请重试');
  });
  
  // 播放结束后清空
  audio.onended = () => {
    if (state.currentAudio === audio) {
      state.currentAudio = null;
    }
  };
}

function stopAudio() {
  if (state.currentAudio) {
    state.currentAudio.pause();
    state.currentAudio = null;
  }
}

// 创建播放按钮HTML
function audioButton(audioPath, label = '') {
  if (!audioPath) return '';
  return `<button class="audio-btn" onclick="playAudio('${audioPath}')" title="${label || '播放语音'}">🔊</button>`;
}

// ==================== 原有代码 ====================

bindEvents();
initRoomFromUrl(); // 检查URL参数自动填充房间号
// 不在页面加载时播放音乐，只在进入房间时播放
// setMusic(state.musicOn); // 移除自动播放
if (state.user) {
  loadHall().then(() => showView('hall'));
} else {
  $('#openIdInput').value = `demo_${Math.random().toString(16).slice(2, 8)}`;
}
