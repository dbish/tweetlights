var highlights = new Set() 
var highlightsToAdd = new Set()
var highlightsToRemove = new Set()
var tweetsState = {};

function getTweet(){
	var tweetID = document.getElementById('tweetID').value;
	var searchTweet = document.getElementById('searchTweet');
	searchTweet.removeChild(searchTweet.firstChild)
	if (!(tweetID in tweetsState)){
		tweetsState[tweetID] = "~highlighted_saved";
	}
	searchTweet.appendChild(createBrowseT(tweetID));
}

function clearUnsavedHighlights(){
	highlightsToRemove.clear();
	highlightsToAdd.clear();
	$(".highlightT.unsaved").each(function(){
		var tweetID = $(this).find('.tweet').attr('tweetid');
		if ($(this).hasClass('unhighlighted')){
			tweetsState[tweetID] = "~highlighted_saved"; 
			$(this).remove();

		}else{
	//		$(this).removeClass('unsaved');
			tweetsState[tweetID] = "highlighted_saved"; 
		}
		updateClasses(tweetID);
	});
}

function createTweet(id){
	var tweet = document.createElement("div");
	$(tweet).addClass('tweet');
	$(tweet).addClass(id);
	tweet.setAttribute('tweetid', id);
	twttr.widgets.createTweet(id, tweet);
	return tweet;
}



function addClicked(e){
	var button = e.target;
	var wrapper = $(button).parent();
	var tweetID = $(wrapper).find('.tweet').attr('tweetid');

	switch(tweetsState[tweetID]){
		case "~highlighted_saved":
			tweetsState[tweetID] = "highlighted_~saved";
			document.getElementById('tweets').appendChild(createHighlightT(tweetID));
			highlightsToAdd.add(tweetID);
			break;
		case "~highlighted_~saved":
			tweetsState[tweetID] = "highlighted_saved";
			highlightsToRemove.delete(tweetID);
			break;

	}
	updateClasses(tweetID);

}

function removeClicked(e){
	var button = e.target;
	var wrapper = $(button).parent();
	var tweetID = $(wrapper).find('.tweet').attr('tweetid');

	switch(tweetsState[tweetID]){
		case "highlighted_saved":
			tweetsState[tweetID] = "~highlighted_~saved";
			highlightsToRemove.add(tweetID);
			break;
		case "highlighted_~saved":
			tweetsState[tweetID] = "~highlighted_saved";
			highlightsToAdd.delete(tweetID);
			wrapper.remove();
			break;
	}
	updateClasses(tweetID);
}

function updateClasses(tweetID){
	$('.'+tweetID).each(function(){
		var wrapper = $(this).parent();
		wrapper.removeClass("highlighted unhighlighted unsaved");
		switch(tweetsState[tweetID]){
			case "highlighted_saved":
				wrapper.addClass('highlighted');
				break;
			case "highlighted_~saved":
				wrapper.addClass('highlighted unsaved');
				break;
			case "~highlighted_~saved":
				wrapper.addClass('unhighlighted unsaved');
				break;
		}
		
	});
	if ((highlightsToAdd.size > 0) || (highlightsToRemove.size > 0)){
		$('#saveButton').prop('disabled', false);	
	}else{
		$('#saveButton').prop('disabled', true);	
	}

}

function createTweetWrapper(id){
	var wrapper = document.createElement('div');

	var tweet = createTweet(id);

	var addButton = document.createElement('button');
	addButton.textContent = 'highlight';
	$(addButton).addClass('addButton btn btn-primary btn-sm');
	addButton.addEventListener('click', addClicked, false);

	wrapper.appendChild(tweet);
	wrapper.appendChild(addButton);
	$(wrapper).addClass('shadow p3 mb-5 bg-white rounded')

	switch(tweetsState[id]){
		case "highlighted_saved":
			$(wrapper).addClass('highlighted');
			break;
		case "highlighted_~saved":
			$(wrapper).addClass('highlighted unsaved');
			break;
		case "~highlighted_~saved":
			$(wrapper).addClass('unhighlighted unsaved');
			break;
	}

	return wrapper;
}

function createHighlightT(tweetID){
	var tweetWrapper = createTweetWrapper(tweetID); 

	var removeButton = document.createElement('button');
	removeButton.textContent = 'unhighlight';
	removeButton.addEventListener('click', removeClicked, false);
	$(removeButton).addClass('removeButton btn btn-outline-primary btn-sm');

	tweetWrapper.appendChild(removeButton);
	$(tweetWrapper).addClass('highlightT');

	return tweetWrapper;
}

function createBrowseT(tweetID){
	var tweetWrapper = createTweetWrapper(tweetID);
	return tweetWrapper;
}

function loadHighlightTweets(ids, div){
	var tweetDiv = document.getElementById(div);
	var i;
	for (i in ids){
		tweetsState[ids[i]] = "highlighted_saved";
		tweetDiv.appendChild(createHighlightT(ids[i]));
	}


}

function loadTweets(ids, div){
	var tweetDiv = document.getElementById(div);
	var i;
	for (i in ids){
		if (!(ids[i] in tweetsState)){
			tweetsState[ids[i]] = "~highlighted_saved";
		}
		tweetDiv.appendChild(createBrowseT(ids[i]));
	}
}


