document.getElementById('download-btn').addEventListener('click', function () {
    let zip = new JSZip();
    let folder = zip.folder("images");

    let promises = [];
    document.querySelectorAll('.image-checkbox:checked').forEach(function (checkbox) {
        let imgUrl = checkbox.getAttribute('data-src');
        let imgName = imgUrl.substring(imgUrl.lastIndexOf('/') + 1);

        // Fetch image as blob and add to zip
        let promise = fetch(imgUrl, { mode: 'cors' })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch image: ' + imgUrl);
                }
                return response.blob();
            })
            .then(blob => {
                folder.file(imgName, blob);
            })
            .catch(error => {
                console.error('Error fetching image:', error);
            });

        promises.push(promise);
    });

    // Once all images are fetched and added, generate zip and trigger download
    Promise.all(promises).then(function () {
        zip.generateAsync({ type: "blob" })
            .then(function (content) {
                let link = document.createElement('a');
                link.href = URL.createObjectURL(content);
                link.download = "images.zip";
                link.click();
            })
            .catch(function (error) {
                console.error('Error generating zip:', error);
            });
    });
});