$(document).ready(function() {



    // USER CONFIG POP-UP IMG ONCLICK
    $('.user-img').click(function(event) {
        $('.config-popup').addClass("visible");
        event.stopPropagation();
    });
        // USER CONFIG POP UP GLOBAL
        $(document).click(function(event) {
            if (!$('.config-popup').is(event.target) && $('.config-popup').has(event.target).length === 0) {
                $('.config-popup').removeClass("visible");
            }
        });
 
    // DATA DE HOJE - CHECKBOX
    $('#checkbox-date').on('change', function() {
        if ($(this).is(':checked')) {
          const currentDate = new Date();
          const formattedDate = currentDate.toISOString().slice(0, 10);
          $('#input-date').val(formattedDate);
          $('#input-date').prop('disabled', true);
        } else {
          $('#input-date').val('');
          $('#input-date').prop('disabled', false);
        }
      });
 
    // PLUS TOGGLE BUTTON
  
      $('#togglePlusBtn1').on('click', function() {
          var toggle2 = $(this).find('.icon i');
          var inputThird = $('.input-third');
          var toggle3 = $('#togglePlusBtn2').find('.icon i');
          if (toggle2.hasClass('fa-plus')) {
              toggle2.removeClass('fa-plus').addClass('fa-minus');
              inputThird.addClass('show');
          }
          else if (toggle2.hasClass('fa-minus')) {
              toggle2.removeClass('fa-minus').addClass('fa-plus');
              inputThird.removeClass('show');
              $('.input-fourth').removeClass('show');
          }
          // Remova a classe 'show' do botão da caixa 3
          toggle3.removeClass('fa-minus').addClass('fa-plus');
      });
  
      // PLUS TOGGLE BUTTON (3ª caixa para 4ª caixa)
      $('#togglePlusBtn2').on('click', function() {
 
          var icon = $(this).find('.icon i');
          if (icon.hasClass('fa-plus')) {
              icon.removeClass('fa-plus').addClass('fa-minus');
              $('.input-fourth').addClass('show');
          }
          else if (icon.hasClass('fa-minus')) {
              icon.removeClass('fa-minus').addClass('fa-plus');
              $('.input-fourth').removeClass('show');
          }
      });
 
 
      //APARECER TROCAR SENHA/EMAIL
 
      $('.alterBtn').on('click', function(){
        $('.low-inner-section-div').addClass('after')
      })
 
      //VOLTAR PRA PAGINA ANTERIOR
      $('#goBack').on('click', function(){
        history.back()
      })
 
      //IR PARA A HOME
      $('.logo').on('click', function() {
        window.location.href = '/home/home.html';
      });
 
      //IR PARA CRIE SUA CHART
      $('.new-chart').on('click', function(){
        window.location.href = '/createchart/createchart.html';
      })
 
      //IR PARA RESPONDER PERGUNTAS
      $('.answer-chart').on('click', function(){
        window.location.href = '/adicionarinfo/adicionarinfo.html';
      })
 });