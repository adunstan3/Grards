
const gameCode = JSON.parse(document.getElementById('game-code').textContent);
const userName = JSON.parse(document.getElementById('user-name').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const grardSocket = new ReconnectingWebSocket(
  ws_scheme+
  '://'
  + window.location.host
  + '/ws/grards/game/'
  +gameCode
  +'/'
  +userName
  +'/'
);

grardSocket.onmessage = function(e){
  $(document).ready(function(){
    const data = JSON.parse(e.data);
    if (data.type == 'updatePlayers') {
      console.log(data.players);
      for(i=0; i< data.players.length; i++){
        tempPlayer=data.players[i];

        if(!($("#"+tempPlayer.userName).length)){ //The player doesnt exist
          $('<p id="'+tempPlayer.userName+'" class="'+tempPlayer.state+' general-player">'+tempPlayer.userName+' | '+tempPlayer.points+'</p>').insertBefore(".playerLegend");
            //$(".playerData").append('<p id="'+tempPlayer.userName+'" class="'+tempPlayer.state+' general-player">'+tempPlayer.userName+' | '+tempPlayer.points+'</p>');

        }else if(tempPlayer.toDelete){ //The player should be deleted
          $("#"+tempPlayer.userName).remove();

        }else{ //Update the player
          //update point count
          $("#"+tempPlayer.userName).text(tempPlayer.userName+' | '+tempPlayer.points);
          //update staus
          if(tempPlayer.state == 'grardDefault'){
            $("#"+tempPlayer.userName).removeClass('grardJudge needToPlay').addClass('grardDefault');
          }else if(tempPlayer.state == 'grardJudge'){
            $("#"+tempPlayer.userName).removeClass('grardDefault needToPlay').addClass('grardJudge');
          }else if(tempPlayer.state == 'needToPlay'){
            $("#"+tempPlayer.userName).removeClass('grardDefault grardJudge').addClass('needToPlay');
          }
        }
      }
    //--------------------------------------------------------------------------------------------
    }else if(data.type == 'updateCards'){
      for(i=0; i< data.cards.length; i++){
        tempCard=data.cards[i];
        console.log(tempCard);
        //cycles through card codes till one hasn't been used before
        cardCode='starterCode';
        do{
          cardCode=Math.floor(Math.random()*1000);
        }
        while($("."+cardCode+'container').length);

        console.log(cardCode.toString());
        divString= '<div class="'+cardCode+'container"';
        divString+= 'onmouseenter="grardMouseEnter('+cardCode+')"';
        divString+= 'onmouseleave="grardMouseLeave('+cardCode+')"';
        divString+= 'onclick="grardClick('+cardCode+')"  ></div>'
        $(".playersCards").append(divString);

        $("."+cardCode+"container").append('<label id="'+cardCode+'label" class="generalLabel">'+tempCard+'</label>');
        $("."+cardCode+"container").append('<button type="button" class="'+cardCode+'button generalButton hidden-object" onclick="grardPlay('+cardCode+')" disabled>Play Card</button>');

        //If it is the submission phase enable the new cards
        currentUserName=window.location.href.split('/').slice(-2)[0];

        if($("#"+currentUserName).hasClass("grardDefault")){
          $("."+cardCode+"button").prop('disabled', true);
        }
      }
    //--------------------------------------------------------------------------------------------
    }else if(data.type == 'startRound'){
      console.log(data);
      $("#phaseWaiting").hide();
      $("#phaseSubmit").show();
      $("#phaseJudging").hide();

      $("#startRoundButton").prop('disabled', true);
      $("#startRoundButton").hide();
      $("#toFewPlayers").hide();

      $(".blackCardContainer").show();
      $(".blackCardContainerTital").show();
      $(".blackCardContainer").append("<p class='emptyBlackCard' >"+data.blackCard+"</p>");
      $(".filledBlackCard").remove();

      currentUserName=window.location.href.split('/').slice(-2)[0];


      if(data.judge == currentUserName){
        $("#stopRoundButton").show();
        $("#stopRoundButton").prop('disabled', false);
      }else{
        $("#startRoundButton").hide();
        $(".generalButton").prop('disabled', false);
      }
    //--------------------------------------------------------------------------------------------
    }else if(data.type == 'startJudging'){
      console.log("we have started judging");

      //Determine if this player is the judge
      isJudge=false;
      currentUserName=window.location.href.split('/').slice(-2)[0];
      if(data.judge == currentUserName){
        isJudge=true;
        console.log("You are the judge!");
      }

      $("#phaseWaiting").hide();
      $("#phaseSubmit").hide();
      $("#phaseJudging").show();

      $(".submittedCardsContainer").show();
      $("#stopRoundButton").hide();

      //show submitted cards
      for(i=0; i<data.submitedCards.length; i++){
        tempCard=data.submitedCards[i];
        console.log("tempCard: "+ tempCard);
        //cycles through card codes till one hasn't been used before
        cardCode='starterCode';
        do{
          cardCode=Math.floor(Math.random()*1000);
        }
        while($("."+cardCode+'container').length);

        divString= '<div class="'+cardCode+'container generalSubmissionContainer"';

        if(isJudge){//Only the judge gets interaction privilages
          divString+= 'onmouseenter="grardMouseEnter('+cardCode+')"';
          divString+= 'onmouseleave="grardMouseLeave('+cardCode+')"';
          divString+= 'onclick="grardClick('+cardCode+')"';
        }

        divString+= '></div>'
        $(".submittedCardsContainer").append(divString);

        $("."+cardCode+"container").append('<label id="'+cardCode+'label'+'" class="generalLabel">'+tempCard+'</label>');
        if(isJudge){
          $("."+cardCode+"container").append('<button type="button" class="'+cardCode+'button generalButton hidden-object" onclick="selectWinner('+cardCode+')" >Choose Card</button>');
        }
      }
    //--------------------------------------------------------------------------------------------
    } else if (data.type == 'finishJudging') {
      $("#phaseWaiting").show();
      $("#phaseSubmit").hide();
      $("#phaseJudging").hide();

      $("#startRoundButton").prop('disabled', false);
      $("#startRoundButton").show();

      $(".generalSubmissionContainer").remove();
      $(".submittedCardsContainer").hide();

      $('.generalButton').prop('disabled', true);

      var blackCard = $(".emptyBlackCard").text();

      if(blackCard.includes("_")){
        blackCard = blackCard.replace("___", "<b>"+data.winningCard+"</b>");
      }else{
        blackCard = blackCard+"  <b>"+data.winningCard+"</b>";
      }

      $(".emptyBlackCard").remove();
      $(".blackCardContainerTital").hide();

      if(data.winningPlayer == 'The judge stoped the round with no submissions' || data.winningPlayer == 'The judge left the game before the round was over'){
        $(".blackCardContainer").append("<p class='filledBlackCard'>"+data.winningPlayer+"</p>");
      }else{
        $(".blackCardContainer").append("<p class='filledBlackCard'>"+data.winningPlayer+" won that round </p>");
        $(".blackCardContainer").append("<p class='filledBlackCard'>"+blackCard+"</p>");
      }
    }
  });
};

grardSocket.onclose = function(e){
  console.error('Grard socket closed unexpectedly');
};
