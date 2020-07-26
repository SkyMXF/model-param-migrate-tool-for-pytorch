// load layui module
layui.use(['layer', 'tree', 'util', 'table'], function(){
    var tree = layui.tree
    ,layer = layui.layer
    ,util = layui.util
    ,table = layui.table

    // element
    const srcFileSelect = document.getElementById("src-file-select");
    const aimFileSelect = document.getElementById("aim-file-select");
    const srcTreeView = document.getElementById("srctree");
    const aimTreeView = document.getElementById("aimtree");
    const migrateListView = document.getElementById("migrate-list");
    const addEntryButton = document.getElementById("add-entry-button");
    const removeEntryButton = document.getElementById("remove-entry-button");
    const applyMigrationButton = document.getElementById("apply-migration-button");

    // data
    var nowChosenSrcNode = null;
    var nowChosenAimNode = null;

    eel.refresh_all_data()

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
    };
    update_model_list();

    // add listener for file select elem
    srcFileSelect.addEventListener("change", onChooseSrcPth);
    aimFileSelect.addEventListener("change", onChooseAimPth);

    function onChooseSrcPth(){
        nowChosenSrcNode = null;
        eel.load_src_tree(srcFileSelect.value)().then(
            function(tree_dict){
                tree_dict = parseTreeForView(tree_dict);

                tree.render({
                    elem: '#srctree'
                    ,data: tree_dict
                    ,onlyIconControl: true
                    ,click: function(chosenObj){
                        if (nowChosenSrcNode !== null){
                            nowChosenSrcNode.elem.removeClass("layui-bg-grass");
                        }
                        nowChosenSrcNode = chosenObj;
                        nowChosenSrcNode.elem.addClass("layui-bg-grass");
                    }
                });
            }
        );
    };

    function highlightAllChildren(node){

    };
    function lowlightAllChildren(node){

    };

    function onChooseAimPth(){
        nowChosenAimNode = null;
        eel.load_aim_tree(aimFileSelect.value)().then(
            function(tree_dict){
                tree_dict = parseTreeForView(tree_dict);

                tree.render({
                    elem: '#aimtree'
                    ,data: tree_dict
                    ,onlyIconControl: true
                    ,click: function(chosenObj){
                        if (nowChosenAimNode !== null){
                            nowChosenAimNode.elem.removeClass("layui-bg-skyblue");
                        }
                        nowChosenAimNode = chosenObj;
                        nowChosenAimNode.elem.addClass("layui-bg-skyblue");
                    }
                });
            }
        );
    };

    // function for tree view
    function parseTreeForView(tree_dict){
        return tree_dict;
    };

    // migrate list view
    function updateMigrateListView(migrate_list){
        
        table.render({
            elem: '#migrate-list'
            ,data: migrate_list
            ,cols: [[
                {field:"choose", title:"", type:'checkbox', width:"10%", fixed:"left"}
                ,{field:'src', width:"35%", title: 'src', sort: true}
                ,{field:'aim', width:"35%", title: 'aim', sort: true}
                ,{field:'shape', width: "30%", title: 'shape'}
            ]]
        });
    };
    updateMigrateListView([]);

    // button event
    function addMigrationEntry(){
        if ((nowChosenSrcNode === null) || (nowChosenSrcNode === null)){
            layer.msg("Operation FAILED: Please choose nodes in src and aim params tree first.", {
                time: 10000, // closed after n ms
                btn: ['OK']
            });
            return;
        };
        eel.add_migration_entry(nowChosenSrcNode.data, nowChosenAimNode.data)().then(
            function(data){
                // data: [message, migrate_list]
                message = data[0];
                if (message.length == 0){
                    // if message is empty, operation succeed
                    migrate_list = data[1];
                    updateMigrateListView(migrate_list);
                }
                else{
                    layer.msg(message, {
                        time: 20000, // closed after n ms
                        btn: ['OK']
                    });
                };
            }
        );
    };
    addEntryButton.addEventListener("click", addMigrationEntry);

    function removeMigrationEntry(){
        var listLines = table.cache["migrate-list"];
        var checkedIdxList = [];
        for (var i = 0; i < listLines.length; i++){
            if (listLines[i]["LAY_CHECKED"]){
                checkedIdxList.push(i);
            };
        };
        eel.remove_migration_entry(checkedIdxList)().then(
            function(data){
                // data: [message, migrate_list]
                message = data[0];
                if (message.length == 0){
                    // if message is empty, operation succeed
                    migrate_list = data[1];
                    updateMigrateListView(migrate_list);
                }
                else{
                    layer.msg(message, {
                        time: 20000, // closed after n ms
                        btn: ['OK']
                    });
                };
            }
        );
    };
    removeEntryButton.addEventListener("click", removeMigrationEntry);

    function applyMigration(){
        eel.apply_migration()().then(
            function(data){
                // data: [message, migrate_list]
                message = data[0];
                if (message.length == 0){
                    // if message is empty, operation succeed
                    migrate_list = data[1];
                }
                else{
                    layer.msg(message, {
                        time: 20000, // closed after n ms
                        btn: ['OK']
                    });
                };
                updateMigrateListView(migrate_list);
            }
        );
    };
    applyMigrationButton.addEventListener("click", applyMigration);

});

