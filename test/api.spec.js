// Import the dependencies for testing
const chai = require('chai');
const chaiHttp = require('chai-http');
const app = require('../app');

// Configure chai
chai.use(chaiHttp);
chai.should();

describe("API", () => {
  it("can get assets", (done) => {
    chai.request(app)
      .get('/assets')
      .end((err, res) => {
        res.should.have.status(200);
        res.body.should.be.an('array')
        res.body.should.deep.include({ name: 'Binance USD', chain: 'BNB', symbol: 'BUSD-BD1' })
        done();
      });
  });
});