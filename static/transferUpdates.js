var curSortType;
var index = 10;

function getTweets(idx){
	console.log(curSortType)
	console.log(idx);
	$.post('/getTweets',{
		'sortType':curSortType,
		'index':idx
	}).done(function(response){
		console.log(response);
		loadTweets(response['tweets'], 'previousTweets');
		index = response['index'];
	}).fail(function(){
		console.log('could not contact server');
	});
}

function getMoreTweets(){
	getTweets(index);
}

function sortByRetweets(){
	makeActive('#retweetsButton');
	$('#previousTweets').empty();
	curSortType = 'retweets';
	getTweets(0);
}

function sortByFavorites(){
	makeActive('#favoritesButton');
	$('#previousTweets').empty();
	curSortType = 'favorites';
	getTweets(0);
}

function sortByRecency(){
	makeActive('#recencyButton');
	$('#previousTweets').empty();
	curSortType = 'recency';
	getTweets(0);
}

function sortByScore(){
	makeActive('#scoreButton');
	$('#previousTweets').empty();
	curSortType = 'score';

	getTweets(0);
}

function makeActive(id){
	$('.btn-outline-dark.active').prop('aria-pressed', false);
	$('.btn-outline-dark.active').removeClass('active');
	$(id).prop('aria-pressed', true);
	$(id).addClass('active');
}

function saveHighlights(){
	$.post('/saveHighlights', {

		//data:JSON.stringify(Array.from(highlights)),
		'add':JSON.stringify(Array.from(highlightsToAdd)),
		'remove':JSON.stringify(Array.from(highlightsToRemove))
	}).done(function(response){
		clearUnsavedHighlights();
	}).fail(function(){
		console.log('failure in saving from server');
	});
}

window.onload = function(){
	//loadTweets();
	curSortType = 'recency';
	loadHighlightTweets(collectionTweets, 'tweets');
	loadTweets(startingTweets, 'previousTweets');
};

