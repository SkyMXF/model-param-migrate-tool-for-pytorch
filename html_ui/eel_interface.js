const srcFileSelect = document.getElementById("src-file-select");
const aimFileSelect = document.getElementById("aim-file-select");

// get model list for src and aim model select elem
function update_model_list(){
    eel.eel_get_model_list()().then(
        function(model_list){
            srcFileSelect.length = 1;
            aimFileSelect.length = 1;
            for (var i = 0; i < model_list.length; i++){
                srcFileSelect.options.add(new Option(model_list[i], model_list[i]));
                aimFileSelect.options.add(new Option(model_list[i], model_list[i]));
            }
        }
    );
}
update_model_list();

// add listener for file select elem
srcFileSelect.addEventListener("change", onChooseSrcPth);
aimFileSelect.addEventListener("change", onChooseAimPth);

function onChooseSrcPth(){
    eel.eel_get_tree_view(srcFileSelect.value)().then(
        function(tree_dict){
            tree_dict = parseTreeForView(tree_dict);
            layui.use(['tree', 'util'], function(){
                var tree = layui.tree
                ,layer = layui.layer
                ,util = layui.util

                tree.render({
                    elem: '#srctree'
                    ,data: tree_dict
                    ,showCheckbox: true
                });
            });
        }
    );
};

function onChooseAimPth(){
    eel.eel_get_tree_view(aimFileSelect.value)().then(
        function(tree_dict){
            tree_dict = parseTreeForView(tree_dict);
            layui.use(['tree', 'util'], function(){
                var tree = layui.tree
                ,layer = layui.layer
                ,util = layui.util

                tree.render({
                    elem: '#aimtree'
                    ,data: tree_dict
                    ,showCheckbox: true
                });
            });
        }
    );
};

// function for tree view
function parseTreeForView(tree_dict){
    return tree_dict;
};
