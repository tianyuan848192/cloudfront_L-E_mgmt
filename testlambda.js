exports.handler = (event, context, callback) => {
    const response = {
        status: '200',
        statusDescription: 'OK',
        body: "test",
    };
    callback(null, response);
};