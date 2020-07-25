layui.use(['tree', 'util'], function(){
    var tree = layui.tree
    ,layer = layui.layer
    ,util = layui.util

    //模拟数据3
    ,data3 = [{
        title: 'backbone->encoder'
        ,id: 1
        ,children: [{
            title: 'layer0->layer0'
            ,id: 1000
            ,children: [{
                title: 'conv1->conv1'
                ,id: 10001
                ,children: [{
                    title: 'weight->weight'
                    ,id: 100001
                },{
                    title: 'bias->bias'
                    ,id: 100002
                }]
            }]
        }]
    }]
   
    //按钮事件
    util.event('lay-demo', {
        getChecked: function(othis){
            var checkedData = tree.getChecked('demoId1'); //获取选中节点的数据
            
            layer.alert(JSON.stringify(checkedData), {shade:0});
            console.log(checkedData);
        }
        ,setChecked: function(){
            tree.setChecked('demoId1', [12, 16]); //勾选指定节点
        }
        ,reload: function(){
            //重载实例
            tree.reload('demoId1', {
            
            });
            
        }
    });
    tree.render({
        elem: '#migratetree'
        ,data: data3
        ,showCheckbox: true
    });
});