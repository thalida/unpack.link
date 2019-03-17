let socket = io(window.location.host);

document.addEventListener("DOMContentLoaded", function() {
    console.log(PAGE_CONTEXT.EVENT_KEYS.TREE_UPDATE)
    socket.on(PAGE_CONTEXT.EVENT_KEYS.TREE_UPDATE, function(tree) {
        console.log(tree)
    });
});
