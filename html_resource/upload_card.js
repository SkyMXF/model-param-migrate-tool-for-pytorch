layui.use('upload', function(){
    var $ = layui.jquery
    ,upload = layui.upload;
    
    //选完文件后不自动上传
    upload.render({
        elem: '#test8'
        ,url: 'https://httpbin.org/post' //改成您自己的上传接口
        ,auto: false
        //,multiple: true
        ,bindAction: '#test9'
        ,done: function(res){
        layer.msg('上传成功');
        console.log(res)
        }
    });
    //拖拽上传
    upload.render({
        elem: '#test10'
        ,url: 'https://httpbin.org/post' //改成您自己的上传接口
        ,done: function(res){
        layer.msg('上传成功');
        layui.$('#uploadDemoView').removeClass('layui-hide').find('img').attr('src', res.files.file);
        console.log(res)
        }
    });

});