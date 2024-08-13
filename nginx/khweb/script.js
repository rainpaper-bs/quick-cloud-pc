function getParameterURL(name){
    const url_string = window.location.href;
    const url = new URL(url_string);
    return url.searchParams.get(name);
}
document.getElementById('accountForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var key = document.getElementById('key').value;
    var name = document.getElementById('name').value;
    var pwd = document.getElementById('pwd').value;
    var qq_n = document.getElementById('qq_n').value;
    var qq = getParameterURL("qq_uid");
    var code = getParameterURL("code");
    
    // 构建查询参数字符串
    var queryParams = 'key=' + key + '&name=' + name + '&pwd=' + pwd + '&qq=' + qq + '&code=' + code + '&qq_n=' + qq_n;
    
    // 发送数据到服务器
    fetch('./api?' + queryParams, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        var responseMessage = document.getElementById('responseMessage');
        responseMessage.innerText = data.msg;
        responseMessage.style.color = 'red'; // 设置消息为红色
        alert(data.msg);
    })
    .catch((error) => {
        console.error('错误:', error);
    });
});

document.getElementById('oauthLogin').addEventListener('click', function() {
    // 重定向到后端提供的OAuth2登录URL
    window.location.href = '/oauth';
});