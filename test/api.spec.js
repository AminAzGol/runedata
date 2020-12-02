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

  it("can simulate past data", (done) => {
      var amountInvested = 10000
      var dateInvested = "2020-11-10"
      var pool = "BNB.BULL-BE4"
       
    chai.request(app)
      .post('/past_simulation')
      .send({
          amountInvested,
          dateInvested,
          pool
      })
      .end((err, res) => {
        console.log(res.body.err)
        res.should.have.status(200);
        done();
      });
  });
});