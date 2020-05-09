function getMoreTweets(){
	$.post('/getTweets',{
	}).done(function(response){
		console.log(response);
		loadNewTweets(response);
	}).fail(function(){
		console.log('could not contact server');
	});
}

function saveHighlights(){
	$.post('/saveHighlights', {
		data:JSON.stringify(Array.from(highlights))
	}).done(function(response){
		clearUnsavedHighlights();
	}).fail(function(){
		console.log('failure in saving from server');
	});
}

window.onload = function(){
	//loadTweets();
};

