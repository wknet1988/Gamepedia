// ==================== 背景图管理 ====================
function loadBackgroundFromStorage() {
    const bgData = localStorage.getItem('custom_background');
    if (bgData) {
        document.body.style.backgroundImage = `url(${bgData})`;
        document.body.style.backgroundRepeat = 'repeat';
        document.body.style.backgroundSize = 'auto';
        document.body.classList.add('custom-bg');
    } else {
        document.body.style.backgroundImage = '';
        document.body.classList.remove('custom-bg');
    }
}

function saveBackgroundImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const imgData = e.target.result;
        localStorage.setItem('custom_background', imgData);
        document.body.style.backgroundImage = `url(${imgData})`;
        document.body.style.backgroundRepeat = 'repeat';
        document.body.classList.add('custom-bg');
        if (settingsMessage) settingsMessage.innerText = '背景图已更新';
    };
    reader.readAsDataURL(file);
}

function clearBackground() {
    localStorage.removeItem('custom_background');
    document.body.style.backgroundImage = '';
    document.body.classList.remove('custom-bg');
    if (settingsMessage) settingsMessage.innerText = '背景已移除';
}