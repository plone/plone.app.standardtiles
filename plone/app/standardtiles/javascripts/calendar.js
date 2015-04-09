jQuery(function($) {
   $('.calendar-tile-change-month').on('click', function(e) {

       e.preventDefault();
       $.ajax({
         url: $(this).attr('href'),
         context: $(this).parents('.calendar-tile:first').
           parents('span:first').get(0),
         dataType: 'html',

         success: function(data) {
           domdata = $.mosaic.getDomTreeFromHtml(data).find('.temp_body_tag');
           $(this).html(domdata.html());
         },

         error: function(request, status, error) {
           console.error(error, status, request);
         }
       });

     });
 });
