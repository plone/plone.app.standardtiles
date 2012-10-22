$(document).ready(function() {
	var standardTiles = $('.standardTile', window.parent.document);
	standardTiles.each(function() {
	  var standardTile = $(this);
	  var ploneTile = standardTile.parents('[data-tile]').ploneTile();
	  ploneTile.show();
	});
});
