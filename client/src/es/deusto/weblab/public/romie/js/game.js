showQuestion = function(question)
{
	$('#questionLabel').html(question["question"]);

	question["answers"].forEach(function(answer)
	{
		$('#question .modal-body ul').append('<li>'+answer+"</li>");
	})
	$("#question").modal({keyboard:false});
}