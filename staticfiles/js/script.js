// copy text to clipboard 
function copy_text_to_clipboard() {
    // Get the text content of the div element
    const summaryText = document.getElementById("smart_report_x").textContent;
  
    // Create a temporary textarea element
    const tempTextarea = document.createElement("textarea");
    tempTextarea.value = summaryText;
  
    // Append the textarea to the document body
    document.body.appendChild(tempTextarea);
  
    // Select the text inside the textarea
    tempTextarea.select();
  
    // Copy the selected text to the clipboard
    document.execCommand("copy");
  
    // Remove the temporary textarea from the document body
    document.body.removeChild(tempTextarea);
  
    // Alert the user that the text has been copied
    alert("Summary copied to clipboard! Please wait 30 seconds to download in PDF format.");

    download_pdf();
  }

// download and save file 
function download_file() {
  const boardId = "your_board_id";
  var pdf_status = document.querySelector("#pdf_status");
  pdf_status.style.display = "block";
  const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

  fetch("/api/download/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ board_id: board_id }),
  })
    .then((response) => response.blob())
    .then((blob) => {
      // Create a temporary URL for the blob
      const url = URL.createObjectURL(blob);

      // Create a link element and set its attributes
      const link = document.createElement("a");
      link.href = url;
      link.download = "output.pdf";

      // Append the link to the document body and click it programmatically
      document.body.appendChild(link);
      console.log(url);
      link.click();

      // Clean up the temporary URL
      URL.revokeObjectURL(url);
      pdf_status.style.display = "none";
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// create item 
function create_item() {
  const board_name_x = document.getElementById('board_name');
  const url = '/api/create_board/';
  const data = {
      board_name: board_name_x.value,
  };
  
  const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  
  fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(data => {
        console.log(data)
        location.assign("/dashboard/" + data.board_id + "/")
      })
      .catch(error => console.error(error));
}

// delete item 
function delete_item() {
  const url = "/api/delete_item/";

  const data = {
    board_id: board_id,
  };

  const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      var jsonData = data.output;
      location.reload();
    })
    .catch((error) => console.error(error));
}

// Switch to fullscreen
function switch_fullscreen() {
  const element = document.documentElement; 
  if (element.requestFullscreen) {
    element.requestFullscreen();
  } else if (element.webkitRequestFullscreen) {
    /* Safari */
    element.webkitRequestFullscreen();
  } else if (element.msRequestFullscreen) {
    /* IE11 */
    element.msRequestFullscreen();
  }
}


function page_reload() {
  location.reload();
}
