document.getElementById('startRoundButton').onclick = function(e){
  $(document).ready(function(){
    console.log($(".playerData").children('p').length.toString())
    if($(".playerData").children('p').length >= 3){ //if there are enough players to start a game.
      $('#startRoundButton').prop('disabled', true);

      grardSocket.send(JSON.stringify({
        'toDo' : 'startRound',
      }))
    }else{
      $("#toFewPlayers").show();
    }
  });
}

document.getElementById('stopRoundButton').onclick = function(e){
  $(document).ready(function(){
    $('#stopRoundButton').hide();
    $('#stopRoundButton').prop('disabled', true);
  });

  grardSocket.send(JSON.stringify({
    'toDo' : 'stopRound',
  }))
}


function grardMouseEnter(id){
  $(document).ready(function(){
    $('.'+id+'button').removeClass("hidden-object");
    $('#'+id+'label').addClass('selectedGrard');
  });
}

function grardMouseLeave(id){
  $(document).ready(function(){
    $('.'+id+'button').addClass("hidden-object");
    $('#'+id+'label').removeClass('selectedGrard');
  });
}

function grardClick(id){
  $(document).ready(function(){
    $('.generalButton').addClass("hidden-object");
    $('.generalLabel').removeClass('selectedGrard');
    $('.'+id+'button').removeClass("hidden-object");
    $('#'+id+'label').addClass('selectedGrard');
  });
}

function grardPlay(id){
  cardToPlay=document.getElementById(id+"label").innerHTML;
  $(document).ready(function(){

    $('#'+id+'label').remove();
    $('#'+id+'label').remove();
    $('.'+id+'button').remove();
    $('.'+id+'container').remove();
    $('.'+id+'container').remove();

    console.log("A card has been played: "+cardToPlay);
    $('.generalButton').prop('disabled', true);
    grardSocket.send(JSON.stringify({
      'toDo' : 'playCard',
      'cardToPlay': cardToPlay,
    }))
  });
}

function selectWinner(id){
  winningCard=document.getElementById(id+"label").innerHTML;
  console.log("A winning card has been chosen: "+winningCard);
  $(document).ready(function(){
    $('.generalButton').prop('disabled', true);
  });

  grardSocket.send(JSON.stringify({
    'toDo' : 'endJudging',
    'winningCard': winningCard,
  }))
}
