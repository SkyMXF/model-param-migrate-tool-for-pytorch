layui.use(['tree', 'util'], function(){
    var tree = layui.tree
    ,layer = layui.layer
    ,util = layui.util
    
    //模拟数据1
    ,data1 = [{
        title: 'backbone'
        ,id: 1
        ,children: [{
            title: 'layer0'
            ,id: 1000
            ,children: [{
                title: 'conv1'
                ,id: 10001
                ,children: [{
                    title: 'weight'
                    ,id: 100001
                },{
                    title: 'bias'
                    ,id: 100002
                }]
            },{
                title: 'conv2'
                ,id: 10002
            }]
        },{
            title: 'layer1'
            ,id: 1001
        },{
            title: 'layer2'
            ,id: 1002
        }]
    },{
        title: 'decoder'
        ,id: 2
        ,children: [{
            title: 'layer0'
            ,id: 2000
        },{
            title: 'layer1'
            ,id: 2001
        }]
    },{
        title: 'NMS'
        ,id: 3
        ,children: [{
            title: 'conv1'
            ,id: 3000
        },{
            title: 'conv2'
            ,id: 3001
        }]
    }]
    
    //模拟数据2
    ,data2 = [{
        title: 'encoder'
        ,id: 1
        ,children: [{
            title: 'layer0'
            ,id: 1000
            ,children: [{
                title: 'conv1'
                ,id: 10001
                ,children: [{
                    title: 'weight'
                    ,id: 100001
                },{
                    title: 'bias'
                    ,id: 100002
                }]
            },{
                title: 'conv2'
                ,id: 10002
            }]
        },{
            title: 'layer1'
            ,id: 1001
            ,children: [{
                title: 'conv1'
                ,id: 10001
                ,children: [{
                    title: 'weight'
                    ,id: 100001
                },{
                    title: 'bias'
                    ,id: 100002
                }]
            }]
        },{
            title: 'layer2'
            ,id: 1002
        }]
    },{
        title: 'decoder'
        ,id: 2
        ,children: [{
            title: 'layer0'
            ,id: 2000
        },{
            title: 'layer1'
            ,id: 2001
        }]
    }]

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
   
    //开启复选框
    tree.render({
        elem: '#srctree'
        ,data: data1
        ,showCheckbox: true
    });
    tree.render({
        elem: '#aimtree'
        ,data: data2
        ,showCheckbox: true
    });
    tree.render({
        elem: '#migratetree'
        ,data: data3
        ,showCheckbox: true
    });
});