
// #region finders
function find(keywords) {
    return document.querySelector(keywords)
}
function findAll(keywords) {
    return document.querySelectorAll(keywords)
}
// #endregion

// #region makers
function make(elementName, attrs, content) {
    let element = `<${elementName}`
    Object.entries(attrs).forEach(entry => {
        element += ` ${entry[0]}="${entry[1]}"`
    });
    element += `>${content}</${elementName}>`
    return element
}
// #endregion
