pragma solidity ^0.8.7;

contract BallotChain{

    constructor() {
        electionAdmin = msg.sender;
        electionState = ElectionState.Started;
        totalVoters=0;
        totalCandidates=0;
        countVoteCasted=0;

    }

    address public electionAdmin;
    uint256 public totalVoters;
    uint256 public totalCandidates;
    uint256 public countVoteCasted;

    struct Voter{
        address voterAddress;
        bool hasVoted;
        bool isVoter;

    }
    struct Candidate{
        address candidateAddress;
        uint256 totalVotes;
        bool isCandidate;
    }

    struct VotingData{
        address voterAddress;
        address candidateAddress;
    }
    
    struct Result{
    VotingData data;
    }
    
    enum ElectionState { Started, Voting, Ended } 
    ElectionState public electionState;


    mapping(address=>Voter) public voters; //Creates key-value pairs
    mapping(address=>Candidate) public candidates;
    Voter[] public votersArray;
    Candidate[] public candidatesArray;
    Result[] electionResultArray;
    
    
    //Modifiers
    modifier adminOnly(){
        require(msg.sender == electionAdmin, "Only election admin has access.");
        _;
    }

    modifier inState(ElectionState _state){
        require(electionState == _state, "In Election Phase");
        _;
    }

    modifier notVoted(){
        require(voters[msg.sender].hasVoted == false, "Current user has already voted.");
        _;
    }

    modifier isVoter(){
        require(voters[msg.sender].isVoter, "User is not voter");
        _;
    }


    event voterAdded(address _voter);
    event candidateAdded(address _candidate);
    event electionStarted();
    event castDone(address _voter);
    event electionEnded();

    function addVoter(address _voterAddress) public inState(ElectionState.Started) adminOnly returns (address){
        require(!voters[_voterAddress].isVoter, "Voter is already registerd in system");
        voters[_voterAddress] = Voter({
            voterAddress: _voterAddress,
            hasVoted: false,
            isVoter: true
        });
        totalVoters++;
        emit voterAdded(_voterAddress);
        votersArray.push(voters[_voterAddress]);
        return voters[_voterAddress].voterAddress;
    }

    function removeVoter(address _voterAddress) public inState(ElectionState.Started) adminOnly returns(bool){
        require(voters[_voterAddress].isVoter, "Voter with address is not in the system");
        delete voters[_voterAddress];
        if (candidates[_voterAddress].isCandidate){
            delete candidates[_voterAddress];
        }
        return true;
    }

    function addCandidate(address _candidateAddress) public inState(ElectionState.Started) adminOnly returns(address){
        require(!candidates[_candidateAddress].isCandidate, "Candidate is already registered in system");
        candidates[_candidateAddress] = Candidate({
            candidateAddress: _candidateAddress,
            isCandidate: true,
            totalVotes: 0
        });
        totalCandidates++;
        emit candidateAdded(candidates[_candidateAddress].candidateAddress);
        candidatesArray.push(candidates[_candidateAddress]);
        return candidates[_candidateAddress].candidateAddress;
    }

    function startElection() public inState(ElectionState.Started) adminOnly {
        electionState = ElectionState.Voting;
        emit electionStarted();
    }
    
    function castVote(address _candidateAddress) public inState(ElectionState.Voting) notVoted isVoter {
        require(candidates[_candidateAddress].isCandidate, "User can vote to candidate only");
        voters[msg.sender].hasVoted = true;
        candidates[_candidateAddress].totalVotes++;
        countVoteCasted++;
        
        Result memory res = Result(VotingData(msg.sender, _candidateAddress));
        electionResultArray.push(res);

    }

    function endElection() public inState(ElectionState.Voting) adminOnly returns(uint256){
        electionState = ElectionState.Started;
        emit electionEnded();
        return countVoteCasted;
    }

    function electionResult() external view inState(ElectionState.Voting) returns(Result[] memory){
        
        return electionResultArray;
    } 
}