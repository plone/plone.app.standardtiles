$(document).ready(function() {
	var standardTile = $('.standardTile', window.parent.document);
	var ploneTile = standardTile.parents('[data-tile]').ploneTile();
	ploneTile.show();
});
